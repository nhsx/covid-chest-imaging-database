
import logging
from pathlib import Path
from datetime import datetime

import boto3


logging.basicConfig(level=logging.INFO)


TEMPLATES_DIRECTORY = Path("templates")

CLIENT = boto3.client("cloudformation", region_name="eu-west-2")


def _stack_exists(stack_name):
    response = CLIENT.describe_stacks()
    stack_names = {
        stack_description["StackName"]
        for stack_description in response["Stacks"]
    }
    return stack_name in stack_names


def create_warehouse():
    template_body = (TEMPLATES_DIRECTORY / "warehouse.yaml").read_text()
    timestamp_suffix = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    changeset_name = f"warehouse-{timestamp_suffix}"
    stack_name = "warehouse"
    changeset_type = "UPDATE" if _stack_exists(stack_name) else "CREATE"
    response = CLIENT.create_change_set(
        StackName="warehouse",
        TemplateBody=template_body,
        ChangeSetName=changeset_name,
        ChangeSetType=changeset_type
    )
    changeset_arn = response["Id"]
    return changeset_arn


def main():
    changeset_arn = create_warehouse()
    logging.info(f"Created changeset for warehouse with ARN: {changeset_arn}")


if __name__ == "__main__":
    main()
