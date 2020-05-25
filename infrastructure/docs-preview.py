#!/usr/bin/env python3

import argparse
import logging
from datetime import datetime
from pathlib import Path

import boto3

logging.basicConfig(level=logging.INFO)


TEMPLATES_DIRECTORY = Path("templates")
DEFAULT_TEMPLATE_NAME = "docs-preview"
DEFAULT_BUCKET_NAME = "nhsx-covid-chest-imaging-database-preview"

CLIENT = boto3.client("cloudformation", region_name="eu-west-2")


def _stack_exists(stack_name):
    response = CLIENT.describe_stacks()
    stack_names = {
        stack_description["StackName"] for stack_description in response["Stacks"]
    }
    return stack_name in stack_names


def create_docs_preview_bucket(bucket_name=DEFAULT_BUCKET_NAME):
    template_body = (TEMPLATES_DIRECTORY / "docs-preview.yaml").read_text()
    timestamp_suffix = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    changeset_name = f"{DEFAULT_TEMPLATE_NAME}-{timestamp_suffix}"
    stack_name = f"{DEFAULT_TEMPLATE_NAME}-{bucket_name}"
    logging.info(f"Stack name: {stack_name}")

    # Update or create as needed
    changeset_type = "UPDATE" if _stack_exists(stack_name) else "CREATE"

    # Construct template parameters
    parameters = [
        {"ParameterKey": "BucketNameParameter", "ParameterValue": bucket_name}
    ]

    # Submit the change set
    response = CLIENT.create_change_set(
        StackName=stack_name,
        TemplateBody=template_body,
        ChangeSetName=changeset_name,
        ChangeSetType=changeset_type,
        Capabilities=["CAPABILITY_NAMED_IAM"],
        Parameters=parameters,
    )
    changeset_arn = response["Id"]
    return changeset_arn


def main(bucket_name):
    changeset_arn = create_docs_preview_bucket(bucket_name)
    logging.info(f"Created changeset for docs preview bucket with ARN: {changeset_arn}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b",
        "--bucket",
        help="The docs preview bucket's name",
        default=DEFAULT_BUCKET_NAME,
    )
    args = parser.parse_args()

    main(args.bucket)
