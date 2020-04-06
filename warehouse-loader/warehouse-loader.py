from io import BytesIO
import json
import hashlib
import os
from pathlib import Path
import re
import tempfile

import bonobo
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


def process_image(obj):
    """ Processing images from the raw dump

    Takes a single image, downloads it into temporary storage
    and extracts its metadata.

    The metadata is then uploaded here, except if the file already exists.

    If the image file already exists at the correct location, it's not passed
    on to the next step.
    
    :param obj: the object in queustion
    :type key: boto3.resource('s3').ObjectSummary
    :return: the original object, and a new key where it should be copied within the bucket
    :rtype: (boto3.resource('s3').ObjectSummary, string)
    """
    result = (None, None)
    tmp = BytesIO()
    obj.Object().download_fileobj(tmp)
    tmp.seek(0)
    image_data = pydicom.dcmread(tmp)
    patient_id = image_data["PatientID"].value
    date = get_date_from_key(obj.key, RAW_PREFIX)
    if date:
        training_set = patient_in_training_set(patient_id)
        prefix = TRAINING_PREFIX if training_set else VALIDATION_PREFIX
        new_key = f"{prefix}{patient_id}/images/{date}/{Path(obj.key).name}"
        image_uuid = Path(obj.key).stem
        metadata_key = f"{prefix}{patient_id}/images_metadata/{date}/{image_uuid}.json"
        if not object_exists(metadata_key):
            # upload metadata
            bucket.put_object(
                Body=json.dumps(image_data.to_json_dict()), Key=metadata_key
            )
        if not object_exists(new_key):
            result = (obj, new_key)
    return result


def process_patient_data(obj):
    """ Processing patient data from the raw dump

    Get the patient ID from the filename, do a training/validation
    test split, and create the key for the new location for the
    next processing step to copy things to.
    
    :param obj: the object in queustion
    :type obj: boto3.resource('s3').ObjectSummary 
    :return: the original object, and a new key where it should be copied within the bucket
    :rtype: (boto3.resource('s3').ObjectSummary, string)
    """
    result = (None, None)
    filename = Path(obj.key).name
    patient_id = Path(obj.key).stem
    training_set = patient_in_training_set(patient_id)
    prefix = TRAINING_PREFIX if training_set else VALIDATION_PREFIX
    date = get_date_from_key(obj.key, RAW_PREFIX)
    if date:
        new_key = f"{prefix}{patient_id}/data/{date}/data.json"
        if not object_exists(new_key):
            result = (obj, new_key)
    return result


def process_files(obj):
    """ Generic file processing step

    Split the processing according to the file type,
    and pass on the results to the next step
    
    :param obj: the object in queustion
    :type obj: boto3.resource('s3').ObjectSummary 
    :return: the original object, and a new key where it should be copied within the bucket
    :rtype: (boto3.resource('s3').ObjectSummary, string)
    """
    if Path(obj.key).suffix.lower() == ".dcm":
        yield process_image(obj)
    elif Path(obj.key).suffix.lower() == ".json":
        yield process_patient_data(obj)


def data_copy(obj, new_key):
    """ Copy objects within the bucket

    Only if both original object and new key is provided.
    
    :param obj: the object key in queustion
    :type obj: boto3.resource('s3').ObjectSummary
    :return: standard constant for bonobo "load" steps, so they can be chained
    :rtype: bonobo.constants.NOT_MODIFIED
    """
    if obj is not None and new_key is not None:
        bucket.copy({"Bucket": obj.bucket_name, "Key": obj.key}, new_key)
    return bonobo.constants.NOT_MODIFIED


def get_graph(**options):
    """
    This function builds the graph that needs to be executed.

    :return: bonobo.Graph
    """
    graph = bonobo.Graph(
        extract_raw_folders, extract_raw_files_from_folder, process_files, data_copy,
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
    return {}


# The __main__ block actually execute the graph.
if __name__ == "__main__":
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**options), services=get_services(**options))
