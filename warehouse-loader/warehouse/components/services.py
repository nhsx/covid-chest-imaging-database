import logging
from pathlib import Path
import mondrian
import boto3
import pandas as pd
import tempfile

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
        return self.config.get("raw_prefixes", [])

    def get_training_percentage(self):
        return self.config.get("training_percentage", TRAINING_PERCENTAGE)

    def get_site_group(self, submitting_centre):
        return self.sites.get(submitting_centre)


class DuplicateKeyError(LookupError):
    pass


class KeyCache:
    """ Basic cache for looking up existing files in the bucket
    """

    def __init__(self):
        self.store = set()

    def add(self, key):
        """ Add a key to store in the cache, both the full
        key, and the "filename" part, for different lookups
        """
        lookup_key = Path(key)
        filename = lookup_key.name
        if lookup_key in self.store or filename in self.store:
            raise DuplicateKeyError(
                f"{lookup_key} seems duplicate, danger of overwriting things!"
            )
        else:
            self.store.add(lookup_key)
            self.store.add(filename)

    def exists(self, key, fullpath=False):
        """ Look up a key in the cache, either the "filename"
        alone (default), or the full path
        """
        search_key = Path(key) if fullpath else Path(key).name
        return search_key in self.store


class PatientCache:
    """ Basic cache for looking up existing patients in the bucket
    """

    def __init__(self):
        self.store = dict()

    def add(self, patient_id, group=None):
        if patient_id not in self.store:
            self.store[patient_id] = group
            logger.debug(f"Adding {patient_id} to {group} group")
        elif self.store[patient_id] != group:
            logger.warning(
                f"Found patient with ambiguous groups: {patient_id}; "
                + f"stored group: {self.store[patient_id]}; "
                + f"attempted group: {group}; "
            )

    def get_group(self, patient_id):
        return self.store.get(patient_id)


class SubFolderList:
    """ Managing a list of folder names to include in queries.
    """

    def __init__(self, folder_list=None):
        if folder_list is not None:
            self.folder_list = folder_list
        else:
            self.folder_list = ["data/", "images/"]

    def get(self):
        return self.folder_list


class Inventory:
    def __init__(self, main_bucket=None):
        self.enabled = main_bucket is not None

        if not self.enabled:
            logger.info("Not using inventory.")
        else:
            try:
                inventory_bucket = main_bucket + "-inventory"
                s3_client = boto3.client("s3")
                # Get the latest list of inventory files
                objs = s3_client.list_objects_v2(
                    Bucket=inventory_bucket,
                    Prefix=f"{main_bucket}/daily-full-inventory/hive",
                )["Contents"]
                latest_symlink = sorted([obj["Key"] for obj in objs])[-1]
                header_list = ["bucket", "key", "size", "date"]
                response = s3_client.get_object(
                    Bucket=inventory_bucket, Key=latest_symlink
                )
                frames = []
                for line in (
                    response["Body"].read().decode("utf-8").split("\n")
                ):
                    inventory_file = line.replace(
                        f"s3://{inventory_bucket}/", ""
                    )
                    logger.debug(
                        f"Downloading inventory file: {inventory_file}"
                    )
                    with tempfile.NamedTemporaryFile(mode="w+b") as f:
                        s3_client.download_fileobj(
                            inventory_bucket, inventory_file, f
                        )
                        f.seek(0)
                        frames += [
                            pd.read_csv(
                                f,
                                compression="gzip",
                                error_bad_lines=False,
                                names=header_list,
                            )
                        ]
                self.df = pd.concat(frames, ignore_index=True)
                # This should reduce memory usage, since "bucket" is only a single value
                self.df = self.df.astype({"bucket": "category"})
                # Reduce memory usage by dropping unused column
                header_drop_list = [
                    header
                    for header in header_list
                    if header not in {"bucket", "key"}
                ]
                for header in header_drop_list:
                    self.df.drop(columns=[header], inplace=True)
                logger.info(f"Using inventory: {len(self.df)} items")
            except Exception as e:  # noqa: E722
                logger.warn(f"Skip using inventory due to run time error: {e}")
                self.enabled = False

    def enabled(self):
        """Check whether the inventory is to be used or not
        """
        return self.enabled

    def _filter_iter(self, Prefix):
        """Get an iterator to of known objects with a given prefix
        that can be used by the actual filter functions after transformation
        """
        if not self.enabled:
            return
        for _, row in self.df[
            self.df["key"].str.startswith(Prefix)
        ].iterrows():
            yield row

    def filter_keys(self, Prefix):
        """Get an iterator of object keys with a given prefix
        """
        for obj in self._filter_iter(Prefix=Prefix):
            yield obj["key"]

    def filter(self, Prefix):
        """Get an interator of objects with a given prefix
        """
        # Use a single resource for the filter which speeds things up
        s3 = boto3.resource("s3")
        for obj in self._filter_iter(Prefix=Prefix):
            yield s3.ObjectSummary(obj["bucket"], obj["key"])

    def list_folders(self, Prefix):
        """List the folders just below the given prefix,
        listing including the prefix + folder name.
        """
        if not self.enabled:
            return
        return (
            self.df["key"]
            .str.extract(pat=rf"({Prefix}[^/]*/?).*", expand=False)
            .dropna()
            .unique()
            .tolist()
        )
