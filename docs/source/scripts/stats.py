import csv
import datetime
import os
import sys

import boto3
import pandas as pd

WAREHOUSE_BUCKET = os.getenv("AWS_WAREHOUSE_BUCKET")
if WAREHOUSE_BUCKET is None:
    sys.exit(
        "No bucket info is provided (via the AWS_WAREHOUSE_BUCKET env var)"
    )

PROCESSED_BUCKET = f"{WAREHOUSE_BUCKET}-processed"
INVENTORY_BUCKET = f"{WAREHOUSE_BUCKET}-inventory"


def load_training_data(archive, df):
    path = df.at[archive, "path"]
    data = pd.read_csv(f"s3://{PROCESSED_BUCKET}/{path}", low_memory=False)
    return data[data["group"] == "training"]


def load_inventory(prefixes):
    s3_client = boto3.client("s3")
    # Get the latest list of inventory files
    objs = s3_client.list_objects_v2(
        Bucket=INVENTORY_BUCKET,
        Prefix=f"{WAREHOUSE_BUCKET}/daily-full-inventory/hive",
    )["Contents"]
    latest_symlink = sorted([obj["Key"] for obj in objs])[-1]
    header_list = ["bucket", "key", "size", "date"]
    response = s3_client.get_object(
        Bucket=INVENTORY_BUCKET, Key=latest_symlink
    )
    prefix_sums = {key: 0 for key in prefixes}
    for inventory_file in response["Body"].read().decode("utf-8").split("\n"):
        inventory_file_name = inventory_file.replace(
            f"s3://{INVENTORY_BUCKET}/", ""
        )
        print(f"Downloading inventory file: {inventory_file_name}")
        data = pd.read_csv(
            inventory_file,
            low_memory=False,
            names=["bucket", "key", "size", "date"],
        )
        for prefix in prefixes:
            prefix_sums[prefix] += data[data["key"].str.startswith(prefix)][
                "size"
            ].sum()
    return prefix_sums


df = pd.read_csv(f"s3://{PROCESSED_BUCKET}/latest.csv")
df = df.set_index(["archive"])

output = [["Metric", "Value"]]

patient_clean = load_training_data("patient_clean", df)
ct = load_training_data("ct", df)
mri = load_training_data("mri", df)
xray = load_training_data("xray", df)

# Patients metrics
patients_with_images = (
    set(ct["Pseudonym"]) | set(mri["Pseudonym"]) | set(xray["Pseudonym"])
)
patients_training_positive = set(
    patient_clean[patient_clean["filename_covid_status"]]["Pseudonym"]
)
patients_training_negative = set(
    patient_clean[~patient_clean["filename_covid_status"]]["Pseudonym"]
)

count_patients_training_positive_images = len(
    patients_training_positive & patients_with_images
)
count_patients_training_negative_images = len(
    patients_training_negative & patients_with_images
)

date_cutoff = datetime.datetime.now() - datetime.timedelta(30)
recent_patients = sum(
    pd.to_datetime(patient_clean["filename_earliest_date"]) >= date_cutoff
)

output += [
    [
        "**Total number of patients with images**",
        f"**{count_patients_training_positive_images+count_patients_training_negative_images:,.0f}**",
    ],
    [
        "Positive patients with images",
        f"{count_patients_training_positive_images:,.0f}",
    ],
    [
        "Negative patients with images",
        f"{count_patients_training_negative_images:,.0f}",
    ],
    ["New patients added in the last 30 days", f"{recent_patients:,.0f}"],
    ["", ""],
]

# Images metrics
ct_studies = ct["StudyInstanceUID"].nunique()
mri_studies = mri["StudyInstanceUID"].nunique()
xray_studies = xray["StudyInstanceUID"].nunique()

img_counts = {
    "CT image studies": ct_studies,
    "MRI image studies": mri_studies,
    "X-ray image studies": xray_studies,
}

sorted_img_counts = list(
    map(
        lambda item: [item[0], f"{item[1]:,.0f}"],
        sorted(
            [[item, img_counts[item]] for item in img_counts],
            key=lambda item: item[1],
            reverse=True,
        ),
    )
)

output += [
    [
        "**Total number of image studies**",
        f"**{ct_studies+mri_studies+xray_studies:,.0f}**",
    ]
]
output += sorted_img_counts
output += [["", ""]]

# Data storage metrics
prefix_sums = load_inventory(
    ["training/ct/", "training/xray/", "training/mri/", "training/"]
)

total_storage = prefix_sums["training/"] / (1024 ** 3)
data_storage = {
    "CT image storage": prefix_sums["training/ct/"] / (1024 ** 3),
    "MRI image storage": prefix_sums["training/mri/"] / (1024 ** 3),
    "X-ray image storage": prefix_sums["training/xray/"] / (1024 ** 3),
}

sorted_data_storage = list(
    map(
        lambda item: [item[0], f"{item[1]:,.0f}GB"],
        sorted(
            [[item, data_storage[item]] for item in data_storage],
            key=lambda item: item[1],
            reverse=True,
        ),
    )
)

output += [
    [
        "**Total image, image metadata, and clinical data storage**",
        f"**{total_storage:,.0f}GB**",
    ]
]
output += sorted_data_storage
output += [["", ""]]

# Submitting centres metrics
nhs_trusts = patient_clean["SubmittingCentre"].nunique()
output += [
    ["**Submitting centres (e.g. NHS trusts)**", f"**{nhs_trusts:,.0f}**"],
]


with open("stats.csv", "w") as csvfile:
    statswriter = csv.writer(
        csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    statswriter.writerows(output)

with open("stats_date.txt", "w") as fragment:
    now = datetime.datetime.now()
    fragment.write(
        f"*This information was last updated on {now.strftime('%-d %B %Y')}.*"
    )
