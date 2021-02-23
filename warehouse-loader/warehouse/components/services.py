import csv
import gzip
import logging
import re
import sys
import tempfile

import boto3
import mondrian

from warehouse.components.constants import TRAINING_PERCENTAGE

mondrian.setup(excepthook=True)
logger = logging.getLogger()


class PipelineConfig:
    """ Configuration settings for the whole pipeline
    """

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
        self.config = input_config
        # Preprocess site groups
        for group in self.config["sites"].keys():
            for site in self.config["sites"][group]:
                self.sites[site] = group
        logger.debug(f"Training percentage: {self.get_training_percentage()}%")

    def get_raw_prefixes(self):
        return set(self.config.get("raw_prefixes", []))

    def get_training_percentage(self):
        return self.config.get("training_percentage", TRAINING_PERCENTAGE)

    def get_site_group(self, submitting_centre):
        return self.sites.get(submitting_centre)


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

    def get_inventory(self, excludeline={}):
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
        return self.main_bucket


class PatientCache:
    def __init__(self, downloader):
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
                        key_match.group("group") == "training",
                    )

    def add(self, patient_id, group):
        if patient_id not in self.store:
            self.store[patient_id] = group == "training"
        elif self.store[patient_id] != group == "training":
            logger.warning(
                f"Found patient with ambiguous groups: {patient_id}; "
            )

    def get_group(self, patient_id):
        group = None
        try:
            group = "training" if self.store[patient_id] else "validation"
        except KeyError:
            # Not Cached
            pass
        return group


class FileList:
    def __init__(self, downloader):
        # set up this downloader outselves?
        self.downloader = downloader
        self.bucket = downloader.get_bucket()

    def get_raw_data_list(self, raw_prefixes=set()):
        pattern = re.compile(
            r"^(?P<raw_prefix>raw-.*)/(\d{4}-\d{2}-\d{2})/data/(?P<filename>[^/]*)$"
        )
        s3 = boto3.resource("s3")
        for r, fragment_reader in self.downloader.get_inventory():
            for row in fragment_reader:
                key = row[1]
                key_match = pattern.match(key)
                if key_match and key_match.group("raw_prefix") in raw_prefixes:
                    yield s3.ObjectSummary(self.bucket, key)

    def get_pending_raw_images_list(self, raw_prefixes=set()):
        raw_pattern = re.compile(
            r"^(?P<raw_prefix>raw-.*)/(\d{4}-\d{2}-\d{2})/images/(?P<filename>[^/]*)$"
        )
        processed_pattern = re.compile(
            r"^(training|validation)/(xray|ct|mri).*/(?P<filename>[^/]*)$"
        )
        s3 = boto3.resource("s3")
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
                yield s3.ObjectSummary(self.bucket, raw_list[unproc])

    def get_processed_data_list(self):
        pattern = re.compile(
            r"^(training|validation)/data/.*/(?P<filename>[^/]*)$"
        )
        s3 = boto3.resource("s3")
        for f, fragment_reader in self.downloader.get_inventory():
            for row in fragment_reader:
                key = row[1]
                key_match = pattern.match(key)
                if key_match:
                    yield s3.ObjectSummary(self.bucket, key)

    def get_processed_images_list(self):
        # Only a single image per study, keep track of studies
        # TODO
        pass
