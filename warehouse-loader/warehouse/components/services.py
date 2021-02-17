import logging
from pathlib import Path
import mondrian
import boto3
import tempfile
import sys
import sqlite3
import gzip
import csv
import re
import os
import pandas as pd

import time
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


def get_inventory(main_bucket):
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
        for line in response["Body"].read().decode("utf-8").split("\n"):
            inventory_file = line.replace(f"s3://{inventory_bucket}/", "")
            logger.debug(f"Downloading inventory file: {inventory_file}")
            with tempfile.TemporaryFile(mode="w+b") as f:
                s3_client.download_fileobj(inventory_bucket, inventory_file, f)
                f.seek(0)
                with gzip.open(f, mode="rt") as cf:
                    reader = csv.reader(cf)
                    yield reader
    except Exception as e:  # noqa: E722
        logger.error(f"Can't use inventory due to run time error: {e}")
        sys.exit(1)


def get_inventory2(main_bucket):
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
        for line in response["Body"].read().decode("utf-8").split("\n"):
            yield pd.read_csv(
                line,
                compression="gzip",
                error_bad_lines=False,
                names=header_list,
                usecols=["key"],
            )

            # inventory_file = line.replace(f"s3://{inventory_bucket}/", "")
            # logger.debug(f"Downloading inventory file: {inventory_file}")
            # with tempfile.TemporaryFile(mode="w+b") as f:
            #     s3_client.download_fileobj(inventory_bucket, inventory_file, f)
            #     f.seek(0)
            #     yield pd.read_csv(
            #         f,
            #         compression="gzip",
            #         error_bad_lines=False,
            #         names=header_list,
            #         usecols=["key"],
            #     )
    except Exception as e:  # noqa: E722
        logger.error(f"Can't use inventory due to run time error: {e}")
        sys.exit(1)


class Caches:
    def __init__(self, main_bucket, dbfile="filecache.db"):
        self.bucket = main_bucket
        self.dbfile = dbfile

        # Patient cache storage dict
        self.patients = {}

        # Database setup
        if os.path.exists(self.dbfile):
            print(f"The database file exists, removing: {self.dbfile}")
            os.remove(self.dbfile)
        else:
            print(f"The database file does not exist: {self.dbfile}")

        self.conn = sqlite3.connect(self.dbfile, check_same_thread=False)
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS paths (filename text)""")
        c.execute("""CREATE INDEX fni ON paths (filename)""")
        self.conn.commit()

        self._load_caches()

    def _load_caches(self):
        processed_pattern = re.compile(
            r"^(training|validation)/(xray|ct|mri).*$"
        )
        patient_pattern = re.compile(
            r"^(?P<set>training|validation)/data/(?P<pseudonym>[^/]*)/.*$"
        )
        n_fragment = 1
        for fragment_reader in get_inventory(self.bucket):
            print(f"Inventory fragment {n_fragment}")
            filenames = []
            for row in fragment_reader:
                # Processed file cache
                item = processed_pattern.match(row[1])
                if item:
                    filenames += [(row[1].split("/")[-1],)]
                    continue
                # Patient cache
                patient = patient_pattern.match(row[1])
                if patient:
                    self.add_patient_to_group(
                        patient.group("pseudonym"), patient.group("set")
                    )

            n_fragment += 1
            c = self.conn.cursor()
            c.executemany("INSERT INTO paths VALUES (?)", filenames)
            self.conn.commit()

    ## Patient cache functions
    def add_patient_to_group(self, pseudonym, group):
        self.patients[pseudonym] = group == "training"

    def get_patient_group(self, pseudonym):
        group = None
        try:
            group = "training" if self.patients[pseudonym] else "validation"
        except KeyError:
            # Not Cached
            pass
        return group

    # File cache functions
    def processed_file_exists(self, filename):
        # start = time.time()
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM paths WHERE filename=? LIMIT 1", (filename,))
        result = c.fetchone() != None
        # print(f"Time {time.time() - start}")
        return result


class FileList:
    def __init__(self, main_bucket):
        self.bucket = main_bucket
        self.pattern = re.compile(
            r"^(?P<raw_prefix>raw-.*)/(\d{4}-\d{2}-\d{2})/(?P<subfolder>data|images)/.*$"
        )

    def get_raw_file_list(
        self, raw_prefixes={}, subfolders={"data", "images"}
    ):
        s3 = boto3.resource("s3")
        for fragment_reader in get_inventory(self.bucket):
            for row in fragment_reader:
                key = row[1]
                key_match = self.pattern.match(key)
                if (
                    key_match
                    and key_match.group("raw_prefix") in raw_prefixes
                    and key_match.group("subfolder") in subfolders
                ):
                    yield s3.ObjectSummary(self.bucket, key)


class ProcessingList:
    def __init__(self, main_bucket):
        self.bucket = main_bucket
        # self.pattern = re.compile(
        #     r"^(?P<raw_prefix>raw-.*)/(\d{4}-\d{2}-\d{2})/(?P<subfolder>data|images)/.*$"
        # )
        self.pattern = re.compile(
            r"^(?P<raw_prefix>raw-.*)/(\d{4}-\d{2}-\d{2})/images/(?P<filename>[^/]*)$"
        )
        # self.processed_pattern = re.compile(
        #     r"^(training|validation)/(xray|ct|mri).*$"
        # )
        self.processed_pattern = re.compile(
            r"^(training|validation)/(xray|ct|mri).*/(?P<filename>[^/]*)$"
        )

    def get_raw_file_list(self, raw_prefixes={}):
        r = 1
        for fragment_reader in get_inventory(self.bucket):
            print(f"Raw fragment {r}")
            startr = time.time()
            raw_list = {}
            for row in fragment_reader:
                key = row[1]
                key_match = self.pattern.match(key)
                if key_match and key_match.group("raw_prefix") in raw_prefixes:
                    raw_list[key_match.group("filename")] = key

            unprocessed = set(raw_list.keys())
            unprocessed_json = {
                key.replace(".dcm", ".json") for key in unprocessed
            }
            print(f"Processing: {time.time() - startr:.3f}s")
            print(len(unprocessed))
            if len(unprocessed) == 0:
                r += 1
                continue

            f = 1
            for fragment_reader2 in get_inventory(self.bucket):
                print(f"Processed fragment {f}")
                startf = time.time()
                filenames = set()
                for row in fragment_reader2:
                    # Processed file cache
                    item = self.processed_pattern.match(row[1])
                    if item:
                        filenames |= {item.group("filename")}
                unprocessed = unprocessed - filenames
                unprocessed_json = unprocessed_json - filenames
                print(f"Processing: {time.time() - startf:.3f}s")
                print(f"Processed files in batch {f}: {len(filenames)}")
                f += 1
                if len(unprocessed) == 0 and len(unprocessed_json) == 0:
                    break

            print(len(unprocessed), len(unprocessed_json))
            unprocessed |= {
                key.replace(".json", ".dcm") for key in unprocessed_json
            }
            for unproc in unprocessed:
                yield (raw_list[unproc])
            r += 1


class ProcessingList2:
    def __init__(self, main_bucket):
        self.bucket = main_bucket
        # self.pattern = re.compile(
        #     r"^(?P<raw_prefix>raw-.*)/(\d{4}-\d{2}-\d{2})/(?P<subfolder>data|images)/.*$"
        # )
        # self.pattern = re.compile(
        #     r"^(?P<raw_prefix>raw-.*)/(\d{4}-\d{2}-\d{2})/images/(?P<filename>[^/]*)$"
        # )
        # self.processed_pattern = re.compile(
        #     r"^(training|validation)/(xray|ct|mri).*$"
        # )

    def get_raw_file_list(self, raw_prefixes={}, subfolders={"images"}):
        self.pattern = re.compile(
            rf"^(?P<raw_prefix>"
            + "|".join(raw_prefixes)
            + r")/(\d{4}-\d{2}-\d{2})/images/(?P<filename>[^/]*)$"
        )
        self.processed_pattern = re.compile(
            r"^(training|validation)/(xray|ct|mri).*$"
        )
        r = 1
        for df_fragment in get_inventory2(self.bucket):
            print(f"Raw fragment {r}")
            startr = time.time()
            df_fragment = df_fragment[
                df_fragment["key"].str.match(self.pattern)
            ]
            df_fragment["filename"] = df_fragment["key"].apply(
                lambda x: x.split("/")[-1]
            )

            unprocessed = set(df_fragment["filename"])
            unprocessed_json = {
                key.replace(".dcm", ".json") for key in unprocessed
            }
            print(f"Processing: {time.time() - startr:.3f}s")
            print(len(unprocessed))
            if len(unprocessed) == 0:
                r += 1
                continue

            f = 1
            for df_fragment2 in get_inventory2(self.bucket):
                print(f"Processed fragment {f}")
                startf = time.time()
                df_fragment2 = df_fragment2[
                    df_fragment2["key"].str.match(self.processed_pattern)
                ]
                filenames = set(
                    df_fragment2["key"].apply(lambda x: x.split("/")[-1])
                )
                unprocessed = unprocessed - filenames
                unprocessed_json = unprocessed_json - filenames
                print(f"Processing: {time.time() - startf:.3f}s")
                print(f"Processed files in batch {f}: {len(filenames)}")
                f += 1
                if len(unprocessed) == 0 and len(unprocessed_json) == 0:
                    break

            print(len(unprocessed), len(unprocessed_json))
            unprocessed |= {
                key.replace(".json", ".dcm") for key in unprocessed_json
            }
            df_results = df_fragment[df_fragment["filename"].isin(unprocessed)]
            for _, key in df_results["key"].iteritems():
                yield key
            r += 1
            # break


# class Inventory:
#     def __init__(self, main_bucket):
#         self.bucket = main_bucket

#         try:
#             inventory_bucket = main_bucket + "-inventory"
#             s3_client = boto3.client("s3")
#             # Get the latest list of inventory files
#             objs = s3_client.list_objects_v2(
#                 Bucket=inventory_bucket,
#                 Prefix=f"{main_bucket}/daily-full-inventory/hive",
#             )["Contents"]
#             latest_symlink = sorted([obj["Key"] for obj in objs])[-1]
#             header_list = ["bucket", "key", "size", "date"]
#             response = s3_client.get_object(
#                 Bucket=inventory_bucket, Key=latest_symlink
#             )
#             for line in (
#                 response["Body"].read().decode("utf-8").split("\n")
#             ):
#                 inventory_file = line.replace(
#                     f"s3://{inventory_bucket}/", ""
#                 )
#                 logger.debug(
#                     f"Downloading inventory file: {inventory_file}"
#                 )
#                 with tempfile.TemporaryFile(mode="w+b") as f:
#                         s3_client.download_fileobj(
#                         inventory_bucket, inventory_file, f
#                     )
#                     f.seek(0)
#                     with gzip.open(f, mode="rt") as cf:
#                         reader = csv.reader(cf)
#                         self.keys |= {row[1] for row in reader}
#         except Exception as e:  # noqa: E722
#             logger.error(f"Can't use inventory due to run time error: {e}")
#             sys.exit(1)

# def enabled(self):
#     """Check whether the inventory is to be used or not
#     """
#     return self.enabled

# def _filter_iter(self, Prefix):
#     """Get an iterator to of known objects with a given prefix
#     that can be used by the actual filter functions after transformation
#     """
#     if not self.enabled:
#         return
#     for _, row in self.df[
#         self.df["key"].str.startswith(Prefix)
#     ].iterrows():
#         yield row

# def filter_keys(self, Prefix):
#     """Get an iterator of object keys with a given prefix
#     """
#     for obj in self._filter_iter(Prefix=Prefix):
#         yield obj["key"]

# def filter(self, Prefix):
#     """Get an interator of objects with a given prefix
#     """
#     # Use a single resource for the filter which speeds things up
#     s3 = boto3.resource("s3")
#     for obj in self._filter_iter(Prefix=Prefix):
#         yield s3.ObjectSummary(obj["bucket"], obj["key"])

# def list_folders(self, Prefix):
#     """List the folders just below the given prefix,
#     listing including the prefix + folder name.
#     """
#     if not self.enabled:
#         return
#     return (
#         self.df["key"]
#         .str.extract(pat=rf"({Prefix}[^/]*/?).*", expand=False)
#         .dropna()
#         .unique()
#         .tolist()
#     )
