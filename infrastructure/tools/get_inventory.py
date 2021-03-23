#!/usr/bin/env python

import argparse
import logging
from pathlib import Path

import boto3

logging.basicConfig(level=logging.INFO)


def download_inventory(main_bucket, output_folder):
    """Downloading the relevant inventory files

    Parameters
    ----------
    main_bucket : str
        The main warehouse bucket name (inventory bucket name
        will be extrapolated from there).
    output_folder : str
        The folder where to download the files.
    """
    inventory_bucket = f"{main_bucket}-inventory"
    s3_client = boto3.client("s3")
    # Get the latest list of inventory files
    objs = s3_client.list_objects_v2(
        Bucket=inventory_bucket, Prefix=f"{main_bucket}/daily-full-inventory/hive",
    )["Contents"]
    latest_symlink = sorted([obj["Key"] for obj in objs])[-1]
    response = s3_client.get_object(Bucket=inventory_bucket, Key=latest_symlink)
    for line in response["Body"].read().decode("utf-8").split("\n"):
        inventory_file = line.replace(f"s3://{inventory_bucket}/", "")
        logging.info(f"Downloading inventory file: {inventory_file}")
        output_path = Path(output_folder) / Path(inventory_file).name
        s3_client.download_file(inventory_bucket, inventory_file, str(output_path))
        logging.info(f"Saved to: {output_path}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Download the latest set of S3 inventory files."
    )
    parser.add_argument(
        "-b",
        "--bucket",
        default="nccid-data-warehouse-prod",
        help="The bucket whose inventory to grab.",
    )
    parser.add_argument(
        "-o",
        "--output-folder",
        default="./",
        help="Where to download the inventory files",
    )
    args = parser.parse_args()
    download_inventory(args.bucket, args.output_folder)
