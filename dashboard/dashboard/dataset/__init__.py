import pandas as pd


class Dataset:
    def __init__(self, data_latest_path):
        self.data = {"ct": None, "mri": None, "xray": None, "patient": None}
        self.data_latest_path = data_latest_path
        self.load_data()

    def get_counter(self):
        return self.counter

    def reset_counter(self):
        self.counter = 0

    def inc_counter(self, step=1):
        self.counter += step

    def load_data(self):
        df = pd.read_csv(self.data_latest_path)
        df = df.set_index(["archive"])

        self.data["ct"] = self._load_training_data("ct", df)
        self.data["mri"] = self._load_training_data("mri", df)
        self.data["xray"] = self._load_training_data("xray", df)
        self.data["patient"] = self._load_training_data("patient_clean", df)
        print(self.data)

    def _load_training_data(self, archive, df):
        base_path = str(self.data_latest_path).rstrip("latest.csv")
        archive_path = f"{base_path}{df.at[archive, 'path']}"
        data = pd.read_csv(archive_path, low_memory=False)
        return data
