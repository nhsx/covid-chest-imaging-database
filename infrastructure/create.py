import argparse
import logging
from pathlib import Path
from datetime import datetime

import boto3

logging.basicConfig(level=logging.INFO)


TEMPLATES_DIRECTORY = Path("templates")
DEFAULT_TEMPLATE_NAME = "warehouse"
DEAFULT_BUCKET_NAME = "nccid-data-warehouse"

CLIENT = boto3.client("cloudformation", region_name="eu-west-2")


def _stack_exists(stack_name):
    response = CLIENT.describe_stacks()
    stack_names = {
        stack_description["StackName"] for stack_description in response["Stacks"]
    }
    return stack_name in stack_names


def create_warehouse(suffix=None):
    suffix_string = "" if suffix is None else f"-{suffix}"
    template_body = (TEMPLATES_DIRECTORY / "warehouse.yaml").read_text()
    timestamp_suffix = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    changeset_name = f"{DEFAULT_TEMPLATE_NAME}-{timestamp_suffix}"
    stack_name = f"{DEFAULT_TEMPLATE_NAME}{suffix_string}"
    logging.info(f"Stack name: {stack_name}")
    bucket_name = f"{DEAFULT_BUCKET_NAME}{suffix_string}"

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


def main(suffix=None):
    changeset_arn = create_warehouse(suffix)
    logging.info(f"Created changeset for warehouse with ARN: {changeset_arn}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--suffix", help="suffix to use for templates and names")
    args = parser.parse_args()

    main(args.suffix)
