import csv
import gzip
import logging
import re
import sys
import tempfile

import boto3
import mondrian
from botocore.exceptions import ClientError

from warehouse.components.constants import TRAINING_PERCENTAGE

mondrian.setup(excepthook=True)
logger = logging.getLogger()


class PipelineConfig:
    """Configuration settings for the whole pipeline"""

    def __init__(self):
        self.config = dict(
            {
                "raw_prefixes": [],
                "training_percentage": TRAINING_PERCENTAGE,
                "sites": {"split": [], "training": [], "validation": []},
            }
        )
        self.sites = dict()

    def set_config(self, input_config):
        """Setting pipeline configuration from supplied data.

        Parameters
        ----------
        input_config : dict
            The configuration to ingest and set internally.
        """
        self.config = input_config
        # Preprocess site groups
        for group in self.config["sites"].keys():
            for site in self.config["sites"][group]:
                self.sites[site] = group
        logger.debug(f"Training percentage: {self.get_training_percentage()}%")

    def get_raw_prefixes(self):
        """Return a set of raw prefixes that the configuration
        is set to process.

        Returns
        -------
        set
            A set of configured "raw-..." prefixes to process by the pipeline
        """
        return set(self.config.get("raw_prefixes", []))

    def get_training_percentage(self):
        """Return set training precentage, either default or configured

        Returns
        -------
        int
            the proportion of random assignment to the training set (0-100)
        """
        training_percent = self.config.get(
            "training_percentage", TRAINING_PERCENTAGE
        )
        if training_percent > 100:
            training_percent = 100
        if training_percent < 0:
            training_percent = 0
        return training_percent

    def get_site_group(self, submitting_centre):
        """Get the group (training/validation) to which a
        submitting centre is assigned for.

        Parameters
        ----------
        submitting_centre : str
            The submitting centre's name to look up

        Returns
        -------
        group : str
            The group (training, validation, split) that the
            given centre is configured for
        """
        return self.sites.get(submitting_centre)


class S3Client:
    def __init__(self, bucket):
        self._bucket = bucket
        self._client = boto3.client("s3")

    @property
    def bucket(self):
        return self._bucket

    @property
    def client(self):
        return self._client

    def object_exists(self, key):
        """Checking whether a given object exists in our work bucket

        Parameters
        ----------
        key : str
            The object key in question.

        Returns
        -------
        boolean
            True if object exists in the work bucket.

        Raises
        ------
        botocore.exceptions.ClientError
            If there's any transfer error.
        """
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise ClientError
        else:
            return True

    def object_content(self, key, content_range=None):
        try:
            args = {"Bucket": self._bucket, "Key": key}
            if content_range is not None:
                args["Range"] = content_range
            file_content = self._client.get_object(**args)["Body"].read()
        except ClientError:
            raise
        return file_content

    def put_object(self, key, content):
        try:
            args = {"Bucket": self._bucket, "Key": key, "Body": content}
            self._client.put_object(**args)
        except ClientError:
            raise

    def copy_object(self, old_key, new_key):
        try:
            args = {
                "Bucket": self._bucket,
                "CopySource": {"Bucket": self._bucket, "Key": old_key},
                "Key": new_key,
            }
            self._client.copy_object(**args)
        except ClientError:
            raise


class InventoryDownloader:
    def __init__(self, main_bucket):
        self.main_bucket = main_bucket
        self.inventory_bucket = self.main_bucket + "-inventory"
        self._get_inventory_list()

    def _get_inventory_list(self):
        try:
            inventory_bucket = self.main_bucket + "-inventory"
            s3_client = boto3.client("s3")
            # Get the latest list of inventory files
            objs = s3_client.list_objects_v2(
                Bucket=inventory_bucket,
                Prefix=f"{self.main_bucket}/daily-full-inventory/hive",
            )["Contents"]
            latest_symlink = sorted([obj["Key"] for obj in objs])[-1]
            response = s3_client.get_object(
                Bucket=inventory_bucket, Key=latest_symlink
            )
            self.inventory_list = [
                line.replace(f"s3://{inventory_bucket}/", "")
                for line in response["Body"].read().decode("utf-8").split("\n")
            ]
        except Exception as e:  # noqa: E722
            logger.error(f"Can't use inventory due to run time error: {e}")
            sys.exit(1)

    def get_inventory(self, excludeline=set()):
        """Iterate through all the inventory files, and passing back a reader
        to use the data from them.

        Parameters
        ----------
        exclideline : set
            Listing all the fragments of the inventory to exclude from reading

        Yields
        ------
        tuple[int, _csv.reader]
            Index of the given inventory fragment and a CSV reader initialized
        """
        try:
            s3_client = boto3.client("s3")
            for index, inventory_file in enumerate(self.inventory_list):
                if index in excludeline:
                    logger.debug(
                        f"Skipping inventory file as requested: {inventory_file}"
                    )
                    continue
                logger.debug(f"Downloading inventory file: {inventory_file}")
                with tempfile.TemporaryFile(mode="w+b") as f:
                    s3_client.download_fileobj(
                        self.inventory_bucket, inventory_file, f
                    )
                    f.seek(0)
                    with gzip.open(f, mode="rt") as cf:
                        reader = csv.reader(cf)
                        yield index, reader
        except Exception as e:  # noqa: E722
            logger.error(f"Can't use inventory due to run time error: {e}")
            sys.exit(1)

    def get_bucket(self):
        """The S3 bucket that this downloader is configured to use.

        Returns
        -------
        str
            S3 bucket name
        """
        return self.main_bucket


class CacheContradiction(Exception):
    pass


class PatientCache:
    """A cache to store group assignments of patient IDs"""

    def __init__(self, downloader):
        """A cache to store group assignments of patient IDs.

        Parameters
        ----------
        downloader: InventoryDownloader
            An initialized downloader instance.
        """
        self.downloader = downloader
        self.store = dict()
        self._load_cache()

    def _load_cache(self):
        pattern = re.compile(
            r"^(?P<group>training|validation)/data/(?P<pseudonym>[^/]*)/[^/]*$"
        )
        for f, fragment_reader in self.downloader.get_inventory():
            for row in fragment_reader:
                key = row[1]
                key_match = pattern.match(key)
                if key_match:
                    self.add(
                        key_match.group("pseudonym"),
                        key_match.group("group"),
                    )

    def add(self, patient_id, group):
        """Add an item to an existing patient cache

        Paramters
        ---------
        patient_id : str
            The patient ID or pseudonym to store
        group : str
            Expected group is "training" or "validation", only stores whether the patient is in the "training group or not.
        """
        if patient_id not in self.store:
            self.store[patient_id] = group == "training"
        elif self.store[patient_id] != (group == "training"):
            raise CacheContradiction(
                f"Found patient with ambiguous groups: {patient_id}"
            )

    def get_group(self, patient_id):
        """Check if a given patient is in "training" or "validation" group,
        or even known to the cache or not.

        Parameters
        ----------
        patient_id : str
            The patient ID / pseudonym in question

        Returns
        -------
        group : str or None
            The values "training" or "validation" if grouping is known, or None if patient is not in cache.
        """
        group = None
        try:
            group = "training" if self.store[patient_id] else "validation"
        except KeyError:
            # Not Cached
            pass
        return group


class FileList:
    def __init__(self, downloader):
        self.downloader = downloader
        self.bucket = downloader.get_bucket()

    def get_raw_data_list(self, raw_prefixes=set()):
        """Get the list of raw data files from the inventory

        Parameters
        ----------
        raw_prefixes : set, default=set()
            The raw prefixes to consider for processing in the warehouse.

        Yields
        ------
        str
            The keys for the raw data files found
        """

        pattern = re.compile(
            r"^(?P<raw_prefix>raw-.*)/(\d{4}-\d{2}-\d{2})/data/(?P<filename>[^/]*)$"
        )
        for r, fragment_reader in self.downloader.get_inventory():
            for row in fragment_reader:
                key = row[1]
                key_match = pattern.match(key)
                if key_match and key_match.group("raw_prefix") in raw_prefixes:
                    yield key

    def get_pending_raw_images_list(self, raw_prefixes=set()):
        """Get the list of raw data files from the inventory

        Parameters
        ----------
        raw_prefixes : set, default=set()
            The raw prefixes to consider for processing in the warehouse.

        Yields
        ------
        str
            The keys for raw image files that seem not yet to be processed.
        """
        raw_pattern = re.compile(
            r"^(?P<raw_prefix>raw-.*)/\d{4}-\d{2}-\d{2}/images/(?P<filename>[^/]*)$"
        )
        processed_pattern = re.compile(
            r"^(training|validation)/(xray|ct|mri).*/(?P<filename>[^/]*)$"
        )
        fragment_excludelist = set()
        for _, fragment_reader in self.downloader.get_inventory():
            raw_list = dict()
            for row in fragment_reader:
                key = row[1]
                key_match = raw_pattern.match(key)
                if key_match and key_match.group("raw_prefix") in raw_prefixes:
                    raw_list[key_match.group("filename")] = key

            unprocessed = set(raw_list.keys())
            unprocessed_json = {
                key.replace(".dcm", ".json") for key in unprocessed
            }
            if len(unprocessed) == 0:
                continue

            for f, fragment_reader2 in self.downloader.get_inventory(
                fragment_excludelist
            ):
                filenames = set()
                for row in fragment_reader2:
                    # Processed file cache
                    item = processed_pattern.match(row[1])
                    if item:
                        filenames.add(item.group("filename"))
                if len(filenames) == 0:
                    fragment_excludelist.add(f)
                unprocessed = unprocessed - filenames
                unprocessed_json = unprocessed_json - filenames
                if len(unprocessed) == 0 and len(unprocessed_json) == 0:
                    break

            unprocessed |= {
                key.replace(".json", ".dcm") for key in unprocessed_json
            }
            for unproc in unprocessed:
                yield raw_list[unproc]

    def get_processed_data_list(self):
        """Getting the list of processed data files from the warehouse

        Yields
        ------
        str
            The keys to the processed data files to look at.
        """
        pattern = re.compile(
            r"^(training|validation)/data/.*/(?P<filename>[^/]*)$"
        )
        for f, fragment_reader in self.downloader.get_inventory():
            for row in fragment_reader:
                key = row[1]
                key_match = pattern.match(key)
                if key_match:
                    yield key

    def get_processed_images_list(self):
        # Only a single image per study, keep track of studies
        # TODO
        pass
