""" This module preprocesses data about the warehouse and makes
it available for further analysis and display.
"""

import json
import logging
import os
import re
from datetime import datetime

import bonobo
import mondrian
import pandas as pd
import pydicom
from bonobo.config import (
    Configurable,
    ContextProcessor,
    Service,
    use,
    use_raw_input,
)
from bonobo.util.objects import ValueHolder
from botocore.exceptions import ClientError
from nccid_cleaning import clean_data_df, patient_df_pipeline

import warehouse.components.services as services

mondrian.setup(excepthook=True)
logger = logging.getLogger()

BUCKET_NAME = os.getenv("WAREHOUSE_BUCKET", default=None)
LOCAL_ONLY = bool(os.getenv("LOCAL_ONLY", default=False))

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


@use("filelist")
def list_clinical_files(filelist):
    """Listing of processed clinical files in the warehouse.

    Parameters
    ----------
    filelist : FileList
        To use to query the contents of the warehouse

    Yields
    ------
    tupe(str, dict)
        The pseudonym and the corresponding dictionary with group and file list info
        (group: str, files: list)
    """
    patients = {}
    pattern = re.compile(
        r"^(?P<group>training|validation)/data/(?P<pseudonym>[^/]+)/(?P<filename>[^/]+\.json)$"
    )
    for data_file in filelist.get_processed_data_list():
        match = pattern.match(data_file)
        if match:
            pseudonym = match.group("pseudonym")
            if pseudonym not in patients:
                patients[pseudonym] = {
                    "group": match.group("group"),
                    "files": [match.group("filename")],
                }
            else:
                patients[pseudonym]["files"] += [match.group("filename")]
                assert match.group("group") == patients[pseudonym]["group"]

    for pseudonym in sorted(patients.keys()):
        yield pseudonym, patients[pseudonym]


@use("s3client")
def load_clinical_files(*args, s3client):
    """Processing of the clinical files in the warehouse.

    Parameters
    ----------
    args : tuple
        pseudonym, data tuple, as passed on by "list_clinical_files"
    s3client : S3Client
        The S3 client set up to interact with the warehouse bucket

    Yields
    ------
    tuple(str, dict)
        The data group name "patient", and the extracted clinical record

    Raises
    ------
    ClientError
        If there's an issue with getting the latest data file
    """
    pseudonym, data = args
    filename_list = data["files"]

    # This relies on the filename format being consistent
    file_dates = [
        datetime.strptime(key.split("_")[1].split(".")[0], "%Y-%m-%d").date()
        for key in filename_list
    ]
    covid_positive = any(
        [filename.lower().startswith("data_") for filename in filename_list]
    )

    file_filter = "data_" if covid_positive else "status_"
    filtered_file_list = sorted(
        [key for key in filename_list if file_filter in key], reverse=True
    )
    assert len(filtered_file_list[0]) > 0

    # Reconstruct the file path for the latest file
    latest_file = f"{data['group']}/data/{pseudonym}/{filtered_file_list[0]}"

    try:
        result = s3client.get_object(key=latest_file)
        # result = s3client.get_object(Bucket=inventory.bucket, Key=latest_file)
    except ClientError as ex:
        if ex.response["Error"]["Code"] == "NoSuchKey":
            logger.error(f"No object found: {latest_file}")
        else:
            raise
        return

    last_modified = result["LastModified"].date()
    file_content = result["Body"].read().decode("utf-8")

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
        "last_modified": last_modified,
        "group": data["group"],
        **latest_record,
    }

    yield "patient", latest_record


@use("filelist")
def list_image_metadata_files(filelist):
    """Listing of processed image metadata files in the warehouse.
    Only lists a single file per imaging study.

    Parameters
    ----------
    filelist : FileList
        To use to query the contents of the warehouse

    Yields
    ------
    tupe(str, str, str)
        group, modality, filename (key) value set
    """
    studies = set()
    pattern = re.compile(
        r"^(?P<group>training|validation)/(?P<modality>[^-/]*)-metadata/(?P<pseudonym>[^/]+)/(?P<studyid>[^/]+)/(?P<seriesid>[^/]+)/(?P<filename>[^/]+\.json)$"
    )
    for processed_file in filelist.get_processed_images_list():
        match = pattern.match(processed_file)
        if match and match.group("studyid") not in studies:
            studies.add(match.group("studyid"))
            yield match.group("group"), match.group("modality"), processed_file


@use("s3client")
def load_image_metadata_files(*args, s3client):
    """Processing of the clinical files in the warehouse.

    Parameters
    ----------
    args : tuple
        group, modality, filename info as passed on by "list_image_metadata_files"
    s3client : S3Client
        The S3 client set up to interact with the warehouse bucket

    Yields
    ------
    tuple(str, dict)
        The data group name (modality) and the extracted image record

    Raises
    ------
    ClientError
        If there's an issue with getting the latest data file
    """
    group, modality, image_file = args
    try:
        result = s3client.get_object(key=image_file)
    except ClientError as ex:
        if ex.response["Error"]["Code"] == "NoSuchKey":
            logger.error(f"No object found: {image_file}")
        else:
            raise
        return

    last_modified = result["LastModified"].date()
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
    record = {
        "Pseudonym": ds.PatientID,
        "group": group,
        "last_modified": last_modified,
    }
    fields_of_interest = DICOM_FIELDS & set(ds.dir())
    record.update(
        {attribute: ds.get(attribute) for attribute in fields_of_interest}
    )
    yield modality, record


def dicom_age_in_years(age_string):
    """Helper function to extract DICOM age into float

    Parameters
    ----------
    age_string : str
        The age string as defined in the DICOM standard,
        see http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.2.html

    Returns
    -------
    float or None
        The age or None if any conversiomn went wrong.
    """
    try:
        units = age_string[-1]
        value = age_string[0:-1]
    except IndexError:
        return
    try:
        age = float(value)
    except ValueError:
        return

    if units == "Y":
        # default
        pass
    elif units == "M":
        age /= 12
    elif units == "W":
        age /= 52
    elif units == "D":
        age = 0
    else:
        # unknown
        return
    return age


def patient_data_dicom_update(patients, images):
    """Fills in missing values for Sex and Age from imaging dicom headers.

    Parameters
    ----------
    patients : pd.DataFrame
        The patient clinical data record that needs filling in.
    images : pd.DataFrame
        The image metadata record.

    Returns
    -------
    pd.DataFrame
        Patient data with updated sex and age information filled in from the images data
    """

    demo = pd.concat(
        [
            modality[["Pseudonym", "PatientSex", "PatientAge"]]
            for modality in images
        ]
    )
    demo["ParsedPatientAge"] = demo["PatientAge"].map(dicom_age_in_years)
    demo_dedup = (
        demo.sort_values("ParsedPatientAge", ascending=True)
        .drop_duplicates(subset=["Pseudonym"], keep="last")
        .sort_index()
    )

    def _fill_sex(x, df_dicom):
        sex = x["sex"]
        if sex == "Unknown":
            try:
                sex = df_dicom.loc[df_dicom["Pseudonym"] == x["Pseudonym"]][
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


@use("inventory")
def get_storage_stats(inventory):
    """Calculate storage metrics from an inventory

    Parameters
    ----------
    inventory : InventoryDownloader
        The service set up for downloading inventory data

    Returns
    -------
    tuple[str, dict]
        The data type "stats", and the metrics as a dictionary
    """
    prefixes = [
        "training/ct/",
        "training/xray/",
        "training/mri/",
        "training/",
        "validation/ct/",
        "validation/xray/",
        "validation/mri/",
        "validation/",
    ]
    prefix_sums = {key: 0 for key in prefixes}

    for _, fragment_reader in inventory.get_inventory():
        for row in fragment_reader:
            key = row[1]
            for prefix in prefixes:
                if key.startswith(prefix):
                    size = int(row[2])
                    prefix_sums[prefix] += size

    yield "stats", prefix_sums


class DataExtractor(Configurable):
    """Get unique submitting centre names from the full database."""

    s3client = Service("s3client_processed")

    @ContextProcessor
    def acc(self, context, *, s3client):
        records = yield ValueHolder(dict())
        # At the end of the processing of all previous nodes,
        # it will continue from here

        values = records.get()
        images = []
        csv_settings = dict(index=False, header=True)
        collection = {"archive": [], "path": []}
        batch_date = datetime.now().isoformat()

        for modality in ["ct", "xray", "mri"]:
            if modality in values:
                df = pd.DataFrame.from_dict(values[modality], orient="index")
                images += [df]
                file_name = f"{modality}.csv"
                output_path = file_name
                df.to_csv(output_path, **csv_settings)
                collection["archive"] += [modality]
                if not LOCAL_ONLY:
                    output_path = f"{batch_date}/{file_name}"
                    s3client.upload_file(output_path, file_name)
                collection["path"] += [output_path]

        patient = pd.DataFrame.from_dict(values["patient"], orient="index")
        file_name = "partient.csv"
        output_path = file_name
        patient.to_csv(output_path, **csv_settings)
        collection["archive"] += ["patient"]
        if not LOCAL_ONLY:
            output_path = f"{batch_date}/{file_name}"
            s3client.upload_file(output_path, file_name)
        collection["path"] += [output_path]

        patient = clean_data_df(patient, patient_df_pipeline)
        patient_clean = patient_data_dicom_update(patient, images)

        file_name = "patient_clean.csv"
        output_path = file_name
        patient_clean.to_csv(output_path, **csv_settings)
        collection["archive"] += ["patient_clean"]
        if not LOCAL_ONLY:
            output_path = f"{batch_date}/{file_name}"
            s3client.upload_file(output_path, file_name)
        collection["path"] += [output_path]

        # Save storate stats
        storage_stats = (
            pd.DataFrame.from_dict(values["stats"])
            .reset_index()
            .rename(columns={"index": "prefix", 0: "storage"})
        )
        file_name = "storage.csv"
        output_path = file_name
        storage_stats.to_csv(output_path, **csv_settings)
        collection["archive"] += ["storage"]
        if not LOCAL_ONLY:
            output_path = f"{batch_date}/{file_name}"
            s3client.upload_file(output_path, file_name)
        collection["path"] += [output_path]

        # Save a list of latest files
        file_name = "latest.csv"
        output_path = file_name
        pd.DataFrame.from_dict(collection, orient="columns").to_csv(
            output_path, **csv_settings
        )
        if not LOCAL_ONLY:
            s3client.upload_file(output_path, file_name)

    @use_raw_input
    def __call__(self, records, *args, **kwargs):
        """The function that is run on each incoming data from the
        It collects information in the stateful value holder, in
        a way that it can be easily processed later.
        """
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
        list_clinical_files,
        load_clinical_files,
        _output="extractor",
    )

    graph.add_chain(
        list_image_metadata_files,
        load_image_metadata_files,
        _output="extractor",
    )

    graph.add_chain(
        get_storage_stats,
        _output="extractor",
    )

    return graph


def get_services(**options):
    """
    This function builds the services dictionary, which is a simple dict of names-to-implementation used by bonobo
    for runtime injection.

    It will be used on top of the defaults provided by bonobo (fs, http, ...). You can override those defaults, or just
    let the framework define them. You can also define your own services and naming is up to you.

    Returns
    -------
    dict
        The mapping of the specific services
    """
    if BUCKET_NAME is None:
        return {
            "filelist": None,
            "inventory": None,
            "s3client": None,
            "s3client_processed": None,
        }

    s3client = services.S3Client(bucket=BUCKET_NAME)
    s3client_processed = services.S3Client(bucket=f"{BUCKET_NAME}-processed")
    inv_downloader = services.InventoryDownloader(main_bucket=BUCKET_NAME)
    filelist = services.FileList(inv_downloader)

    return {
        "filelist": filelist,
        "inventory": inv_downloader,
        "s3client": s3client,
        "s3client_processed": s3client_processed,
    }


def main():
    """Execute the pipeline graph"""
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**options), services=get_services(**options))


# The __main__ block actually execute the graph.
if __name__ == "__main__":
    main()
