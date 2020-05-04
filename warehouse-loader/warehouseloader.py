import hashlib
import itertools
import json
import logging
import os
import re
from io import BytesIO
from pathlib import Path

import bonobo
import boto3
import mondrian
import pydicom
from bonobo.config import Configurable, ContextProcessor, Service, use
from botocore.exceptions import ClientError

# set up logging
mondrian.setup(excepthook=True)
logger = logging.getLogger()

s3_resource = boto3.resource("s3")
s3_client = boto3.client("s3")

BUCKET_NAME = os.getenv("WAREHOUSE_BUCKET", default="chest-data-warehouse")
bucket = s3_resource.Bucket(BUCKET_NAME)

TRAINING_PREFIX = "training/"
VALIDATION_PREFIX = "validation/"
CONFIG_KEY = "config.json"

TRAINING_PERCENTAGE = 0

MODALITY = {
    "DX": "x-ray",
    "CR": "x-ray",
    "MR": "mri",
    "CT": "ct",
}

DRY_RUN = bool(os.getenv("DRY_RUN", default=False))

###
# Services
###
class PipelineConfig:
    """ Basic cache for looking up existing files in the bucket
    """

    def __init__(self):
        self.config = {
            "raw-uploads": {"training-validation": [], "validation-only": []}
        }

    def set_config(self, input_config):
        self.config = input_config
        logger.debug(f"Training percentage: {self.get_training_percentage()}%")

    def get_raw_prefixes(self):
        return self.config.get("raw_prefixes", [])

    def get_training_percentage(self):
        return self.config.get("training_percentage", TRAINING_PERCENTAGE)


class KeyCache:
    """ Basic cache for looking up existing files in the bucket
    """

    def __init__(self):
        self.store = set()

    def add(self, key):
        """ Add a key to store in the cache, both the full
        key, and the "filename" part, for different lookups
        """
        filename = Path(key).name
        if filename in self.store():
            logger.error(f"{filename} seems duplicate, danger of overwriting things!")
        else:
            self.store.add(key)
            self.store.add(filename)

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
    """ Extract date from an object key from the bucket's directory pattern,
    for a given prefix

    :param key: the object key in question
    :type key: string
    :return: the extracted date if found
    :rtype: string or None
    """
    date_match = re.match(r"^.+/(?P<date>\d{4}-\d{2}-\d{2})/.+", key)
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
        int(hashlib.sha512(patient_id.strip().upper().encode("utf-8")).hexdigest(), 16)
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


###
# Transformation steps
###
@use("config")
def load_config(config):
    """Load configuration from the bucket
    """
    try:
        obj = bucket.Object(CONFIG_KEY).get()
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


@use("config")
def extract_raw_folders(config):
    """ Extractor: get all date folders within the `raw/` data drop

    :return: subfolders within the `raw/` prefix (yield)
    :rtype: string
    """
    for site_raw_prefix in config.get_raw_prefixes():
        result = s3_client.list_objects(
            Bucket=BUCKET_NAME, Prefix=site_raw_prefix, Delimiter="/"
        )
        # list folders in reverse order, and since the folders are dates, that will
        # return newer folders first, which are less likely to be already processed
        folders = iter(
            sorted(
                [p.get("Prefix") for p in result.get("CommonPrefixes")], reverse=True
            )
        )
        for f in folders:
            yield f


def extract_raw_files_from_folder(folder):
    """ Extract files from a given date folder in the data dump

    :param folder: the folder to process
    :type key: string
    :return: each object (yield)
    :rtype: boto3.resource('s3').ObjectSummary
    """
    for obj in bucket.objects.filter(Prefix=folder):
        yield obj


@use("keycache")
@use("config")
def process_image(*args, keycache, config):
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
    # check file type
    (obj,) = args
    if Path(obj.key).suffix.lower() != ".dcm":
        # not an image, don't do anything with it
        return

    # check if work is already done
    image_in_cache = keycache.exists(obj.key)
    image_uuid = Path(obj.key).stem
    metadata_in_cache = keycache.exists(f"{image_uuid}.json")
    if metadata_in_cache and image_in_cache:
        # files exist, nothing to do here
        return

    # download the image
    with BytesIO() as tmp:
        obj.Object().download_fileobj(tmp)
        tmp.seek(0)
        image_data = pydicom.dcmread(tmp, stop_before_pixels=True)

    # extract the required data from the image
    patient_id = image_data["PatientID"].value
    image_type = MODALITY.get(image_data["Modality"].value, "unknown")
    training_set = patient_in_training_set(patient_id, config.get_training_percentage())
    prefix = TRAINING_PREFIX if training_set else VALIDATION_PREFIX

    date = get_date_from_key(obj.key)
    if date:
        # the location of the new files
        new_key = f"{prefix}{image_type}/{patient_id}/{Path(obj.key).name}"
        metadata_key = f"{prefix}{image_type}-metadata/{patient_id}/{image_uuid}.json"
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
    task, metadata_key, image_data, = args
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
    task, outgoing_key, outgoing_data, = args
    if task == "upload" and outgoing_key is not None and outgoing_data is not None:
        if DRY_RUN:
            logger.info(f"Would upload to key: {outgoing_key}")
        else:
            bucket.put_object(Body=outgoing_data, Key=outgoing_key)

        return bonobo.constants.NOT_MODIFIED


@use("config")
def process_patient_data(*args, config):
    """Processing patient data from the raw dump

    Get the patient ID from the filename, do a training/validation
    test split, and create the key for the new location for the
    next processing step to copy things to.

    :param obj: the object in question
    :type obj: boto3.resource('s3').ObjectSummary
    :return: a task name, the original object, and a new key where it should be copied within the bucket
    :rtype: (string, boto3.resource('s3').ObjectSummary, string)
    """
    (obj,) = args
    if Path(obj.key).suffix.lower() != ".json":
        # Not a data file, don't do anything with it
        return

    m = re.match(r"^(?P<patient_id>.*)_(?P<outcome>data|status)$", Path(obj.key).stem)
    if m:
        patient_id = m.group("patient_id")
        outcome = m.group("outcome")
        training_set = patient_in_training_set(
            patient_id, config.get_training_percentage()
        )
        prefix = TRAINING_PREFIX if training_set else VALIDATION_PREFIX
        date = get_date_from_key(obj.key)
        if date:
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
    task, obj, new_key, = args
    if task == "copy" and obj is not None and new_key is not None:
        if DRY_RUN:
            logger.info(f"Would copy: {obj.key} -> {new_key}")
        else:
            bucket.copy({"Bucket": obj.bucket_name, "Key": obj.key}, new_key)

        return bonobo.constants.NOT_MODIFIED


def get_summary_date(cache, key):
    """ Get date for a given file from the relevant sources

    :param cache: the cache of the "raw" input to look things up in
    :type cache: dict
    :param key: object key to process
    :type key: string
    :return: the extracted date if any
    :rtype: string or None
    """
    datamatch = re.match(
        r"^.+_(?P<date>\d{4}-\d{2}-\d{2})\.json$", Path(key).name.lower(),
    )
    if datamatch:
        # it's a data file, get date from the filename
        return datamatch.group("date")

    if Path(key).suffix.lower() == ".json":
        # it's a metadata file, look things up by the original DICOM image
        lookup_key = Path(key).stem.lower() + ".dcm"
    else:
        # it's an image
        lookup_key = Path(key).name.lower()
    return cache.get(lookup_key)


def prepare_summary(cache, prefix, modality):
    """

    :param cache: the cache of the "raw input to look things up in
    :type cache: dict
    :param prefix: the prefix to act on (usually "training/" and "validation/"), needs trailing slash
    :type prefix: string
    :param modality: subfolder to look in (such as "ct", "data", ...)
    :type modality: string
    :return: file summary the extracted from the bucket structure
    :rtype: list[dict]
    """
    prefix = prefix + modality + "/"
    modality_files = bucket.objects.filter(Prefix=prefix)
    modality_list = []
    for obj in modality_files:
        file_key = obj.key
        file_name = Path(file_key).name
        date = get_summary_date(cache, file_key)
        patient_match = re.match(rf"^{prefix}(?P<patient_id>.+?)\/.*", file_key)
        if date and patient_match:
            patient_id = patient_match.group("patient_id")
            modality_list += [
                {
                    "patient_id": patient_id,
                    "modality": modality,
                    "file_name": file_name,
                    "file_key": file_key,
                    "upload_date": date,
                }
            ]
    return modality_list


class SummaryFile(Configurable):
    """ Get unique channel names from the raw messages. """

    config = Service("config")

    @ContextProcessor
    def processor(self, context, config, *args):
        """Run at the very end of processing and upload summary
        files to all relevant directories.
        """
        yield

        # When everything else finished, kick off real computation
        cache = {}
        for raw_prefix in config.get_raw_prefixes():
            raw_files = bucket.objects.filter(Prefix=raw_prefix)
            for f in raw_files:
                cache[Path(f.key).name.lower()] = get_date_from_key(f.key)

        modalities = (
            set(["data"])
            | set(MODALITY.values())
            | set([m + "-metadata" for m in MODALITY.values()])
        )
        prefixes = [TRAINING_PREFIX, VALIDATION_PREFIX]

        for prefix, modality in itertools.product(prefixes, modalities):
            summary = json.dumps(prepare_summary(cache, prefix, modality))
            summarykey = prefix + modality + "/summary.json"
            upload = True
            if object_exists(summarykey):
                obj = bucket.Object(summarykey).get()
                contents = obj["Body"].read().decode("utf-8")
                if contents == summary:
                    upload = False
                    logger.debug(
                        f"{summarykey}: already exists and content is current."
                    )
            if upload:
                if DRY_RUN:
                    logger.info(f"Would upload: {summarykey}")
                else:
                    upload_text_data("upload", summarykey, summary)

    def __call__(self, *args, **kwargs):
        # this should be a total no-op
        pass


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
        load_existing_files,
        extract_raw_folders,
        extract_raw_files_from_folder,
    )

    graph.add_chain(SummaryFile(), _input=None, _name="metadata")

    graph.add_chain(data_copy, _input=None, _output="metadata", _name="copy")

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
        process_dicom_data, upload_text_data, _input=process_image, _output="metadata"
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
    config = PipelineConfig()
    return {"keycache": keycache, "config": config}


# The __main__ block actually execute the graph.
if __name__ == "__main__":
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**options), services=get_services(**options))
