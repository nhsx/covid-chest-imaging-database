"""The main warehose pipeline definition.
"""

import hashlib
import json
import logging
import os
import re
import struct
from io import BytesIO
from pathlib import Path, posixpath

import bonobo
import boto3
import mondrian
import pydicom
from bonobo.config import use
from botocore.exceptions import ClientError

from warehouse.components import constants, services

# set up logging
mondrian.setup(excepthook=True)
logger = logging.getLogger()

s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

BUCKET_NAME = os.getenv("WAREHOUSE_BUCKET", default="chest-data-warehouse")
bucket = s3_resource.Bucket(BUCKET_NAME)

DRY_RUN = bool(os.getenv("DRY_RUN", default=False))

KB = 1024

###
# Helpers
###
def object_exists(key):
    """Checking whether a given object exists in our work bucket

    :param key: the object key in question
    :type key: string
    :raises botocore.exceptions.ClientError: if there's any transfer error
    :return: True if object exists in the work bucket
    :rtype: boolean
    """
    try:
        bucket.Object(key).load()
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise ClientError
    else:
        return True


def get_date_from_key(key):
    """Extract date from an object key from the bucket's directory pattern,
    for a given prefix

    :param key: the object key in question
    :type key: string
    :return: the extracted date if found
    :rtype: string or None
    """
    date_match = re.match(r"^.+/(?P<date>\d{4}-\d{2}-\d{2})/.+", key)
    if date_match:
        return date_match.group("date")


def get_submitting_centre_from_object(obj):
    """Extract the SubmittingCentre value from an S3 object that is
    a JSON file in the expected format.

    :param obj: the S3 object of the JSON file to process
    :type obj: boto3.resource('s3').ObjectSummary
    :return: the value defined for SubmittingCentre in the file
    :rtype: string or None
    """
    file_content = obj.Object().get()["Body"].read().decode("utf-8")
    try:
        json_content = json.loads(file_content)
    except json.decoder.JSONDecodeError:
        logger.error("Couldn't decode contents of {obj.key} as JSON.")
        raise
    return json_content.get("SubmittingCentre")


def patient_in_training_set(
    patient_id, training_percent=constants.TRAINING_PERCENTAGE
):
    """Separating patient ID's into training and validation sets, check
    which one this ID should fall into.

    It uses a hashing (sha512) to get pseudo-randomisation based on ID,
    and do the cut-off with a set percentage.

    :param patient_id: the candidate patient ID
    :type patient_id: string
    :param training_percent: the percentage of patience to assign to the training set (defaults to the global TRAINING_PERCENTAGE)
    :type training_percent: int
    :return: True if the patient ID should fall into the training set
    :rtype: boolean
    """
    return (
        int(
            hashlib.sha512(
                patient_id.strip().upper().encode("utf-8")
            ).hexdigest(),
            16,
        )
        % 100
        < training_percent
    )


def inplace_nullify(d, key):
    """
    Recurse through a dictionary and set the value `key` to `None`

    Extracted from https://bitbucket.org/scicomcore/dcm2slimjson/src/master/dcm2slimjson/main.py

    :param d: dict to modify
    :type d: dict
    :param key: specific key to modify
    :type key: anything that can be a dict key
    """
    if isinstance(d, list):
        [inplace_nullify(_, key) for _ in d]

    if isinstance(d, dict):
        for k, v in d.items():

            if k == key:
                d[k] = None

            if isinstance(v, (dict, list)):
                inplace_nullify(v, key)


def scrub_dicom(fd):
    """Remove binary data and other unusuaed sections from a DICOM image.

    Extracted from https://bitbucket.org/scicomcore/dcm2slimjson/src/master/dcm2slimjson/main.py

    :param fd: image data to scrub
    :type fd: pydicom.FileDataset
    :return: the scrubbed image data
    :rtype: dict
    """

    # Use a large value to bypass binary data handler
    out = fd.to_json_dict(bulk_data_threshold=1e20)

    # Drop binary data
    inplace_nullify(out, "InlineBinary")

    # Remove Value of Interest (VOI) transform data
    inplace_nullify(out, "00283010")

    return out


class PartialDicom:
    """Download partial DICOM files iteratively, to save
    on traffic.
    """

    def __init__(self, obj, initial_range_kb=20):
        # Default value of 20Kb initial range is based on
        # tests run on representative data
        self._found_image_tag = False
        self.obj = obj
        self.range_kb = initial_range_kb

    def _stop_when(self, tag, VR, length):
        """Custom stopper for the DICOM reader, to stop
        at the pixel data, but also note whether that
        tag was actually reached.
        """
        self._found_image_tag = tag == (0x7FE0, 0x0010)
        return self._found_image_tag

    def download(self):
        """Download file iteratively, and return the image data"""
        with BytesIO() as tmp:
            while True:
                tmp.seek(0)
                toprange = (self.range_kb * KB) - 1
                stream = self.obj.get(Range=f"bytes=0-{toprange}")["Body"]
                tmp.write(stream.read())
                tmp.seek(0)
                try:
                    image_data = pydicom.filereader.read_partial(
                        tmp, stop_when=self._stop_when
                    )
                    if self._found_image_tag or tmp.tell() < toprange:
                        # We've found the image tag, or there was not image tag
                        # to be found in this image
                        break
                except (OSError, struct.error):
                    # Can happen when file got truncated in the middle of a data field
                    pass
                except Exception:
                    raise
                self.range_kb *= 2
        return image_data


###
# Transformation steps
###
@use("config")
def load_config(config):
    """Load configuration from the bucket"""
    try:
        obj = bucket.Object(constants.CONFIG_KEY).get()
        contents = json.loads(obj["Body"].read().decode("utf-8"))
        config.set_config(contents)
        yield
    except ClientError as ex:
        if ex.response["Error"]["Code"] == "NoSuchKey":
            logger.warning(
                "No configuration found in the bucket! (not going to do any loading)"
            )
        else:
            raise


@use("config")
@use("filelist")
def extract_raw_files_from_folder(config, filelist):
    """Extract files from a given date folder in the data dump

    :param folder: the folder to process
    :type key: string
    :return: each object (yield)
    :rtype: boto3.resource('s3').ObjectSummary
    """
    raw_prefixes = {prefix.rstrip("/") for prefix in config.get_raw_prefixes()}
    # List the clinical data files for processing
    for key in filelist.get_raw_data_list(raw_prefixes=raw_prefixes):
        yield "process", key, None
    # List the unprocessed image files for processing
    for key in filelist.get_pending_raw_images_list(raw_prefixes=raw_prefixes):
        yield "process", key, None


@use("patientcache")
def process_image(*args, patientcache):
    """Processing images from the raw dump

    Takes a single image, downloads it into temporary storage
    and extracts its metadata.

    The metadata is then uploaded here, except if the file already exists.

    If the image file already exists at the correct location, it's not passed
    on to the next step.

    :param obj: the object in question
    :type obj: boto3.resource('s3').ObjectSummary
    :param keycache: the key cache service (provided by bonobo)
    :type keycache: Keycache
    :return: a task name, the original object, and a new key where it should be copied within the bucket
    :rtype: (string, boto3.resource('s3').ObjectSummary, string)
    """
    # check file type
    task, obj, _ = args
    if task != "process" or Path(obj.key).suffix.lower() != ".dcm":
        # not an image, don't do anything with it
        return bonobo.constants.NOT_MODIFIED

    image_path = Path(obj.key)
    image_uuid = image_path.stem

    # download the image
    image_data = PartialDicom(obj.Object()).download()
    if image_data is None:
        # we couldn't read the image data correctly
        logger.warning(
            f"Object '{obj.key}' couldn't be loaded as a DICOM file, skipping!"
        )
        return

    # extract the required data from the image
    patient_id = image_data.PatientID
    study_id = image_data.StudyInstanceUID
    series_id = image_data.SeriesInstanceUID
    group = patientcache.get_group(patient_id)
    if group is not None:
        training_set = group == "training"
    else:
        logger.error(
            f"Image without patient data: {obj.key}; "
            + f"included patient ID: {patient_id}; "
            + "skipping!"
        )
        return
    prefix = (
        constants.TRAINING_PREFIX
        if training_set
        else constants.VALIDATION_PREFIX
    )
    image_type = constants.MODALITY.get(
        image_data["Modality"].value, "unknown"
    )

    date = get_date_from_key(obj.key)
    if date:
        # the location of the new files
        new_key = posixpath.join(
            prefix,
            image_type,
            patient_id,
            study_id,
            series_id,
            Path(obj.key).name,
        )
        metadata_key = posixpath.join(
            prefix,
            f"{image_type}-metadata",
            patient_id,
            study_id,
            series_id,
            f"{image_uuid}.json",
        )
        # send off to copy or upload steps
        if not object_exists(new_key):
            yield "copy", obj, new_key
        if not object_exists(metadata_key):
            yield "metadata", metadata_key, image_data


def process_dicom_data(*args):
    """Process DICOM images, by scrubbing the image data

    :param task: task informatiomn, needs to be equal to "metadata" to be processed here
    :type task: string
    :param metadata_key: location to upload the extracted metadata later
    :type metadata_key: string
    :param image_data: DICOM image data
    :type image_data: pydicom.FileDataset
    :return: metadata key and scrubbed image data, if processed
    :rtype: tuple
    """
    (
        task,
        metadata_key,
        image_data,
    ) = args
    if task == "metadata":
        scrubbed_image_data = scrub_dicom(image_data)
        yield "upload", metadata_key, json.dumps(scrubbed_image_data)


def upload_text_data(*args):
    """Upload the text data to the correct bucket location.

    :param task: selector to run this task or not, needs to be "upload" to process a file
    :type task: string
    :param outgoing_key: location to upload the data
    :type outgoing_key: string
    :param outgoing_data: text to file content to upload
    :type outgoing_data: string
    """
    (
        task,
        outgoing_key,
        outgoing_data,
    ) = args
    if (
        task == "upload"
        and outgoing_key is not None
        and outgoing_data is not None
    ):
        if DRY_RUN:
            logger.info(f"Would upload to key: {outgoing_key}")
        else:
            bucket.put_object(Body=outgoing_data, Key=outgoing_key)

        return bonobo.constants.NOT_MODIFIED


@use("config")
@use("patientcache")
def process_patient_data(*args, config, patientcache):
    """Processing patient data from the raw dump

    Get the patient ID from the filename, do a training/validation
    test split, and create the key for the new location for the
    next processing step to copy things to.

    :param obj: the object in question
    :type obj: boto3.resource('s3').ObjectSummary
    :return: a task name, the original object, and a new key where it should be copied within the bucket
    :rtype: (string, boto3.resource('s3').ObjectSummary, string)
    """
    task, obj, _ = args
    if task != "process" or Path(obj.key).suffix.lower() != ".json":
        # Not a data file, don't do anything with it
        yield bonobo.constants.NOT_MODIFIED

    m = re.match(
        r"^(?P<patient_id>.*)_(?P<outcome>data|status)$", Path(obj.key).stem
    )
    if m is None:
        # Can't interpret this file based on name, skip
        return

    patient_id = m.group("patient_id")
    outcome = m.group("outcome")

    group = patientcache.get_group(patient_id)
    if group is not None:
        training_set = group == "training"
    else:
        # patient group is not cached
        submitting_centre = get_submitting_centre_from_object(obj)
        if submitting_centre is None:
            logger.error(
                f"{obj.key} does not have 'SubmittingCentre' entry, skipping!"
            )
            return

        config_group = config.get_site_group(submitting_centre)
        if config_group is None:
            logger.warning(
                f"Site '{submitting_centre}' is not in configuration, skipping!"
            )
            return
        if config_group == "split":
            training_set = patient_in_training_set(
                patient_id, config.get_training_percentage()
            )
        else:
            # deciding between "training" and "validation" groups.
            training_set = config_group == "training"
        patientcache.add(
            patient_id, "training" if training_set else "validation"
        )

    prefix = (
        constants.TRAINING_PREFIX
        if training_set
        else constants.VALIDATION_PREFIX
    )
    date = get_date_from_key(obj.key)
    if date is not None:
        new_key = f"{prefix}data/{patient_id}/{outcome}_{date}.json"
        if not object_exists(new_key):
            yield "copy", obj, new_key


def data_copy(*args):
    """Copy objects within the bucket

    Only if both original object and new key is provided.

    :param task: selector to run this task or not, needs to be "copy" to process a file
    :type task: string
    :param obj: the object key in question
    :type obj: boto3.resource('s3').ObjectSummary
    :param obj: the new key to copy data to
    :type obj: string
    :return: standard constant for bonobo "load" steps, so they can be chained
    :rtype: bonobo.constants.NOT_MODIFIED
    """
    (
        task,
        obj,
        new_key,
    ) = args
    if task == "copy" and obj is not None and new_key is not None:
        if DRY_RUN:
            logger.info(f"Would copy: {obj.key} -> {new_key}")
        else:
            bucket.copy({"Bucket": obj.bucket_name, "Key": obj.key}, new_key)

        return bonobo.constants.NOT_MODIFIED


###
# Graph setup
###
def get_graph(**options):
    """
    This function builds the graph that needs to be executed.

    :return: bonobo.Graph
    """
    graph = bonobo.Graph()

    graph.add_chain(
        load_config,
        extract_raw_files_from_folder,
    )

    graph.add_chain(data_copy, _input=None, _name="copy")

    graph.add_chain(
        # bonobo.Limit(30),
        process_patient_data,
        _input=extract_raw_files_from_folder,
        _output="copy",
    )

    graph.add_chain(
        # bonobo.Limit(30),
        process_image,
        _input=process_patient_data,
        _output="copy",
    )

    graph.add_chain(process_dicom_data, upload_text_data, _input=process_image)

    return graph


def get_services(**options):
    """
    This function builds the services dictionary, which is a simple dict of names-to-implementation used by bonobo
    for runtime injection.

    It will be used on top of the defaults provided by bonobo (fs, http, ...). You can override those defaults, or just
    let the framework define them. You can also define your own services and naming is up to you.

    :return: dict
    """
    config = services.PipelineConfig()
    inv_downloader = services.InventoryDownloader(main_bucket=BUCKET_NAME)
    patientcache = services.PatientCache(inv_downloader)
    filelist = services.FileList(inv_downloader)

    return {
        "config": config,
        "patientcache": patientcache,
        "filelist": filelist,
    }


def main():
    """Execute the pipeline graph"""
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**options), services=get_services(**options))


if __name__ == "__main__":
    main()
