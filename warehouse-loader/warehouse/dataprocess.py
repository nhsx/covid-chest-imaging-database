""" This module preprocesses data about the warehouse and makes
it available for further analysis and display.
"""

import time

import logging
import os
from pathlib import Path

import bonobo
from bonobo.config import use
import boto3
import mondrian
from bonobo.config import (
    Configurable,
    ContextProcessor,
    Service,
    use_raw_input,
)
from bonobo.util.objects import ValueHolder

import warehouse.warehouseloader as wl  # noqa: E402
from warehouse.components.services import (
    Inventory,
    PipelineConfig,
    SubFolderList,
)

from datetime import datetime
import json
import pandas as pd
import re
import time
import pydicom
from nccid.cleaning import clean_data_df, patient_df_pipeline


mondrian.setup(excepthook=True)
logger = logging.getLogger()

s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

BUCKET_NAME = os.getenv("WAREHOUSE_BUCKET", default="chest-data-warehouse")
bucket = s3_resource.Bucket(BUCKET_NAME)

DRY_RUN = bool(os.getenv("DRY_RUN", default=False))

DICOM_FIELDS = {
    "PatientSex",
    "PatientAge",
    "StudyDate",
    "AcquisitionDate",
    "StudyInstanceUID",
    "SeriesInstanceUID",
    "BodyPartExamined",
    "Manufacturer",
    "ManufacturerModelName",
    "Modality",
}


def get_files_list(file_list, prefix):
    regex = re.compile(rf"^(?P<prefix>.*/)[^/]+$")
    series_prefix = None
    series_files = []
    for file in file_list:
        file_match = regex.match(file)
        if file_match:
            file_prefix = file_match.group("prefix")
            if series_prefix == file_prefix:
                series_files += [file]
            else:
                if series_prefix:
                    # We have some files to share
                    yield series_files
                # start new series
                series_prefix = file_prefix
                series_files = [file]
    if series_files:
        yield series_files


@use("inventory")
def list_clinical_files(inventory):
    for group in ["training", "validation"]:
        # counter = 0
        prefix = f"{group}/data"
        data_files = sorted(inventory.filter_keys(Prefix=prefix))
        for data_list in get_files_list(data_files, prefix):
            # counter += 1
            yield group, data_list
            # if counter >= 1000:
            # break


@use("inventory")
def list_image_metadata_files(inventory):
    for group in ["training", "validation"]:
        for modality in ["ct", "mri", "xray"]:
            # counter = 0
            prefix = f"{group}/{modality}-metadata"
            modality_files = sorted(inventory.filter_keys(Prefix=prefix))
            for series in get_files_list(modality_files, prefix):
                # counter += 1
                yield group, modality, series
                # if counter >= 50:
                # break


@use("inventory")
def load_clinical_files(*args, inventory):
    group, data_list = args
    filename_list = [filename.split("/")[-1] for filename in data_list]

    # This relies on the filename format being consistent
    file_dates = [
        datetime.strptime(key.split("_")[1].split(".")[0], "%Y-%m-%d").date()
        for key in data_list
    ]
    covid_positive = any(
        [filename.lower().startswith("data_") for filename in filename_list]
    )

    file_filter = "data_" if covid_positive else "status_"
    filtered_file_list = sorted(
        [key for key in data_list if file_filter in key], reverse=True
    )
    latest_file = filtered_file_list[0]

    s3_client = boto3.client("s3")
    try:
        result = s3_client.get_object(Bucket=inventory.bucket, Key=latest_file)
    except s3_client.exceptions.NoSuchKey as e:
        logger.info(f"No object found: {latest_file}")
        return

    file_content = result["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)

    latest_record = json.loads(
        file_content,
        object_hook=lambda d: dict(
            d, **d.get("OtherDataSources", {}).get("SegmentationData", {})
        ),
    )

    latest_record = {
        "filename_earliest_date": min(file_dates),
        "filename_covid_status": covid_positive,
        "filename_latest_date": max(file_dates),
        "group": group,
        **latest_record,
    }

    yield "patient", latest_record


@use("inventory")
def load_image_metadata_files(*args, inventory):
    group, modality, series = args
    image_file = series[0]
    s3_client = boto3.client("s3")
    try:
        result = s3_client.get_object(Bucket=inventory.bucket, Key=image_file)
    except s3_client.exceptions.NoSuchKey as e:
        logger.info(f"No object found: {image_file}")
        return

    text = result["Body"].read().decode("utf-8")
    data = json.loads(
        text,
        object_hook=lambda d: {
            k: b"" if k == "InlineBinary" and v is None else v
            for k, v in d.items()
        },
    )
    data = {k: {"vr": "SQ"} if v is None else v for k, v in data.items()}
    ds = pydicom.Dataset.from_json(data)
    record = {"Pseudonym": ds.PatientID, "group": group}
    fields_of_interest = DICOM_FIELDS & set(ds.dir())
    record.update(
        {attribute: ds.get(attribute) for attribute in fields_of_interest}
    )
    yield modality, record


def patient_data_dicom_update(patients, ct, mri, xray) -> pd.DataFrame:
    """
    Fills in missing values for Sex and Age from xray dicom headers.
    """

    demo = pd.concat(
        [
            ct[["Pseudonym", "PatientSex", "PatientAge"]],
            mri[["Pseudonym", "PatientSex", "PatientAge"]],
            xray[["Pseudonym", "PatientSex", "PatientAge"]],
        ]
    )
    demo["ParsedPatientAge"] = demo["PatientAge"].map(
        lambda a: float("".join(filter(str.isdigit, a)))
    )
    demo_dedup = (
        demo.sort_values("ParsedPatientAge", ascending=True)
        .drop_duplicates(subset=["Pseudonym"], keep="last")
        .sort_index()
    )

    def _fill_sex(x, df_dicom):
        sex = x["sex"]
        if sex == "Unknown":
            try:
                age = df_dicom.loc[df_dicom["Pseudonym"] == x["Pseudonym"]][
                    "PatientSex"
                ].values[0]
            except IndexError:
                pass
                # print(f'Pseudonym not in df_dicom data: {x["Pseudonym"]}')
        return sex

    def _fill_age(x, df_dicom):
        age = x["age"]
        if pd.isnull(age):
            try:
                age = df_dicom.loc[df_dicom["Pseudonym"] == x["Pseudonym"]][
                    "ParsedPatientAge"
                ].values[0]
            except IndexError:
                pass
        return age

    patients["age_update"] = patients.apply(
        lambda x: _fill_age(x, demo_dedup), axis=1
    )
    patients["sex_update"] = patients.apply(
        lambda x: _fill_sex(x, demo_dedup), axis=1
    )
    return patients


class DataExtractor(Configurable):
    """Get unique submitting centre names from the full database."""

    inventory = Service("inventory")

    @ContextProcessor
    def acc(self, context, *, inventory):
        records = yield ValueHolder(dict())
        # At the end of the processing of all previous nodes,
        # it will continue from here

        # save some memory
        inventory.purge()

        values = records.get()

        ct = pd.DataFrame.from_dict(values["ct"], orient="index")
        del values["ct"]
        mri = pd.DataFrame.from_dict(values["mri"], orient="index")
        del values["mri"]
        xray = pd.DataFrame.from_dict(values["xray"], orient="index")
        del values["xray"]

        ct.to_csv("ct.csv", index=False, header=True)
        mri.to_csv("mri.csv", index=False, header=True)
        xray.to_csv("xray.csv", index=False, header=True)

        patient = pd.DataFrame.from_dict(values["patient"], orient="index")
        del values["patient"]
        patient.to_csv("patient.csv", index=False, header=True)

        patient = clean_data_df(patient, patient_df_pipeline)

        patient_data_dicom_update(patient, ct, mri, xray).to_csv(
            "patient_clean.csv", index=False, header=True
        )

    @use_raw_input
    def __call__(self, records, *args, **kwargs):
        record_type, record = args
        if record_type not in records:
            records[record_type] = dict()
        records[record_type][len(records[record_type])] = record


###
# Graph setup
###
def get_graph(**options):
    """
    This function builds the graph that needs to be executed.

    :return: bonobo.Graph
    """
    graph = bonobo.Graph()

    graph.add_chain(DataExtractor(), _input=None, _name="extractor")

    graph.add_chain(
        list_clinical_files, load_clinical_files, _output="extractor",
    )

    graph.add_chain(
        list_image_metadata_files,
        load_image_metadata_files,
        _output="extractor",
    )

    return graph


def get_services(**options):
    """
    This function builds the services dictionary, which is a simple dict of names-to-implementation used by bonobo
    for runtime injection.

    It will be used on top of the defaults provided by bonobo (fs, http, ...). You can override those defaults, or just
    let the framework define them. You can also define your own services and naming is up to you.

    :return: dict
    """
    inventory = Inventory(main_bucket=BUCKET_NAME, drop_prefix=["raw-"])

    return {
        "inventory": inventory,
    }


def main():
    """Execute the pipeline graph"""
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**options), services=get_services(**options))


# The __main__ block actually execute the graph.
if __name__ == "__main__":
    main()
