import importlib
import os

import boto3
import pytest
from moto import mock_s3

import warehouse.components.services as services
import warehouse.warehouseloader as warehouseloader


@pytest.mark.parametrize(
    "dryrun",
    [True, False],
)
@mock_s3
def test_data_copy(dryrun):
    old_environ = dict(os.environ)
    if dryrun:
        os.environ.update({"DRY_RUN": "yes"})
    else:
        os.environ.pop("DRY_RUN", default=None)

    importlib.reload(warehouseloader)
    importlib.reload(services)

    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    s3client = services.S3Client(bucket=bucket_name)

    content = "1234567890" * 10
    old_key, new_key = "input.txt", "output.txt"
    s3client.put_object(key=old_key, content=content)
    args = "copy", old_key, new_key
    warehouseloader.data_copy(*args, s3client=s3client)
    if dryrun:
        assert not s3client.object_exists(new_key)
    else:
        assert s3client.object_content(old_key) == s3client.object_content(
            new_key
        )
    os.environ.clear()
    os.environ.update(old_environ)


@pytest.mark.parametrize(
    "dryrun",
    [True, False],
)
@mock_s3
def test_upload_text_data(dryrun):
    old_environ = dict(os.environ)
    if dryrun:
        os.environ.update({"DRY_RUN": "yes"})
    else:
        os.environ.pop("DRY_RUN", default=None)
    importlib.reload(warehouseloader)
    importlib.reload(services)

    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    s3client = services.S3Client(bucket=bucket_name)

    task = "upload"
    key = "test.txt"
    content = "1234567890" * 10

    args = task, key, content
    warehouseloader.upload_text_data(*args, s3client=s3client)
    if dryrun:
        assert not s3client.object_exists(key)
    else:
        assert s3client.object_content(key).decode("utf-8") == content

    os.environ.clear()
    os.environ.update(old_environ)
