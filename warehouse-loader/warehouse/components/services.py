import logging
from pathlib import Path
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
