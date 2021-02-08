import pandas as pd
import time


class Dataset:
    """The dataset that powers the dashboard."""

    def __init__(self, data_latest_path):
        self.data = {
            "ct": None,
            "mri": None,
            "xray": None,
            "patient": None,
            "storage": None,
        }
        self.data_latest_path = data_latest_path
        self.load_data()

    def load_data(self):
        df = pd.read_csv(self.data_latest_path)
        df = df.set_index(["archive"])

        self.data["ct"] = self._load_training_data("ct", df)
        self.data["mri"] = self._load_training_data("mri", df)
        self.data["xray"] = self._load_training_data("xray", df)
        self.data["patient"] = self._load_training_data("patient_clean", df)
        self.data["storage"] = self._load_training_data("storage", df)
        self.last_update_time = time.gmtime()

    def _load_training_data(self, archive, df):
        base_path = str(self.data_latest_path).rstrip("latest.csv")
        archive_path = f"{base_path}{df.at[archive, 'path']}"
        data = pd.read_csv(archive_path, low_memory=False)
        return data

    def get_last_update(self):
        return self.last_update_time
