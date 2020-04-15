from io import BytesIO
import json
import hashlib
import os
from pathlib import Path
import re
import tempfile

import bonobo
from bonobo.config import use
import boto3
from botocore.exceptions import ClientError
import pydicom

s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

BUCKET_NAME = os.getenv("WAREHOUSE_BUCKET", default="chest-data-warehouse")
bucket = s3_resource.Bucket(BUCKET_NAME)

RAW_PREFIX = "raw/"
TRAINING_PREFIX = "training/"
VALIDATION_PREFIX = "validation/"

TRAINING_PERCENTAGE = 60

MODALITY = {
    "DX": "x-ray",
    "CR": "x-ray",
    "MR": "mri",
    "CT": "ct",
}

###
# Services
###
class KeyCache:
    """ Basic cache for looking up existing files in the bucket
    """

    def __init__(self):
        self.store = set()

    def add(self, key):
        """ Add a key to store in the cache, both the full
        key, and the "filename" part, for different lookups
        """
        self.store.add(key)
        self.store.add(Path(key).name)

    def exists(self, key, fullpath=False):
        """ Look up a key in the cache, either the "filename"
        alone (default), or the full path
        """
        if fullpath:
            return Path(key) in self.store
        else:
            return Path(key).name in self.store


###
# Helper functions
###
def object_exists(key):
    """ Checking whether a given object exists in our work bucket
    
    :param key: the object key in queustion
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


def get_date_from_key(key, prefix):
    """ Extract date from an object key from the bucket's directory pattern,
    for a given prefix
    
    :param key: the object key in queustion
    :type key: string 
    :param prefix: the prefix to use, e.g. `raw/`, including the 
    :type prefix: string
    :return: the extracted date if found
    :rtype: string or None
    """
    date_match = re.match(rf"^{prefix}(?P<date>[\d-]*)/.*", key)
    if date_match:
        return date_match.group("date")


def patient_in_training_set(patient_id, training_percent=TRAINING_PERCENTAGE):
    """ Separating patient ID's into training and validation sets, check
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
        int(hashlib.sha512(patient_id.encode("utf-8")).hexdigest(), 16) % 100
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


###
# Transformation steps
###
@use("keycache")
def load_existing_files(keycache):
    """ Loading existing files from the training and
    validation sets into the keycache.

    :param keycache: the key cache service (provided by bonobo)
    :type keycache: Keycache
    """
    for obj in bucket.objects.filter(Prefix=TRAINING_PREFIX):
        keycache.add(obj.key)
    for obj in bucket.objects.filter(Prefix=VALIDATION_PREFIX):
        keycache.add(obj.key)
    return bonobo.constants.NOT_MODIFIED


def extract_raw_folders():
    """ Extractor: get all date folders within the `raw/` data drop

    :return: subfolders within the `raw/` prefix (yield)
    :rtype: string
    """
    result = s3_client.list_objects(
        Bucket=BUCKET_NAME, Prefix=RAW_PREFIX, Delimiter="/"
    )
    for subfolder in result.get("CommonPrefixes"):
        yield subfolder.get("Prefix")


def extract_raw_files_from_folder(folder):
    """ Extract files from a givem date folder in the data dump
    
    :param folder: the folder to process
    :type key: string 
    :return: each object (yield)
    :rtype: boto3.resource('s3').ObjectSummary
    """
    for obj in bucket.objects.filter(Prefix=folder):
        yield obj


@use("keycache")
def process_image(*args, keycache):
    """ Processing images from the raw dump

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
    # print(args)
    (obj,) = args
    if Path(obj.key).suffix.lower() != ".dcm":
        # Not an image, don't do anything with it
        return

    image_in_cache = keycache.exists(obj.key)
    image_uuid = Path(obj.key).stem
    metadata_in_cache = keycache.exists(f"{image_uuid}.json")

    if not metadata_in_cache:
        tmp = BytesIO()
        obj.Object().download_fileobj(tmp)
        tmp.seek(0)
        image_data = pydicom.dcmread(tmp, stop_before_pixels=True)
        patient_id = image_data["PatientID"].value
        image_type = MODALITY.get(image_data["Modality"].value, "unknown")
        date = get_date_from_key(obj.key, RAW_PREFIX)
        if date:
            training_set = patient_in_training_set(patient_id)
            prefix = TRAINING_PREFIX if training_set else VALIDATION_PREFIX
            new_key = f"{prefix}{patient_id}/{image_type}/{Path(obj.key).name}"
            metadata_key = (
                f"{prefix}{patient_id}/{image_type}_metadata/{image_uuid}.json"
            )
            if not object_exists(metadata_key):
                yield "metadata", metadata_key, image_data
    if not metadata_in_cache and not object_exists(new_key):
        yield "copy", obj, new_key


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
    task, metadata_key, image_data, = args
    if task == "metadata":
        scrubbed_image_data = scrub_dicom(image_data)
        yield metadata_key, scrubbed_image_data


def upload_extracted_dicom_data(*args):
    """Upload the extracted DICOM data to the correct bucket
    location.

    :param metadata_key: location to upload the extracted metadata later
    :type metadata_key: string
    :param image_data: scrubbed DICOM image data
    :type image_data: dict
    """
    metadata_key, scrubbed_image_data, = args
    bucket.put_object(Body=json.dumps(scrubbed_image_data), Key=metadata_key)
    return bonobo.constants.NOT_MODIFIED


def process_patient_data(*args):
    """Processing patient data from the raw dump

    Get the patient ID from the filename, do a training/validation
    test split, and create the key for the new location for the
    next processing step to copy things to.
    
    :param obj: the object in queustion
    :type obj: boto3.resource('s3').ObjectSummary 
    :return: a task name, the original object, and a new key where it should be copied within the bucket
    :rtype: (string, boto3.resource('s3').ObjectSummary, string)
    """
    (obj,) = args
    if Path(obj.key).suffix.lower() != ".json":
        # Not a data file, don't do anything with it
        return

    patient_id = Path(obj.key).stem.replace("_data", "").replace("_status", "")
    training_set = patient_in_training_set(patient_id)
    prefix = TRAINING_PREFIX if training_set else VALIDATION_PREFIX
    date = get_date_from_key(obj.key, RAW_PREFIX)
    if date:
        new_key = f"{prefix}{patient_id}/data/{date}/data.json"
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
    task, obj, new_key, = args
    if task != "copy":
        return bonobo.constants.NOT_MODIFIED

    if obj is not None and new_key is not None:
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
        load_existing_files, extract_raw_folders, extract_raw_files_from_folder,
    )

    graph.add_chain(data_copy, _input=None, _name="copy")

    graph.add_chain(
        # bonobo.Limit(30),
        process_image,
        _input=extract_raw_files_from_folder,
        _output="copy",
    )

    graph.add_chain(
        # bonobo.Limit(30),
        process_patient_data,
        _input=extract_raw_files_from_folder,
        _output="copy",
    )

    graph.add_chain(
        process_dicom_data, upload_extracted_dicom_data, _input=process_image
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
    keycache = KeyCache()
    return {"keycache": keycache}


# The __main__ block actually execute the graph.
if __name__ == "__main__":
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**options), services=get_services(**options))
