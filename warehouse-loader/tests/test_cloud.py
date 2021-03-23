import csv
import gzip
import json
import math
import pathlib
import uuid
from io import BytesIO, StringIO

import bonobo
import boto3
import pydicom
import pytest
from botocore.exceptions import ClientError
from moto import mock_s3

import warehouse.components.helpers as helpers
import warehouse.dataprocess as dataprocess
import warehouse.submittingcentres as submittingcentres
import warehouse.warehouseloader as warehouseloader
from warehouse.components.constants import (
    CONFIG_KEY,
    TRAINING_PREFIX,
    VALIDATION_PREFIX,
)
from warehouse.components.services import (
    CacheContradiction,
    FileList,
    InventoryDownloader,
    PatientCache,
    PipelineConfig,
    S3Client,
)
from warehouse.warehouseloader import PartialDicom


###
# Helper
###
def create_inventory(file_name_list, main_bucket_name, batches=1):
    """Helper creating a (mock) inventory from a given file list
    and upload them to the relevant S3 bucket.

    Parameters
    ----------
    file_name_list : list
        Iterable with the filenames to put into the inventory
    main_bucket_name : str
        The main warehouse bucket, against which the inventory is created
    batches : int, default=1
        The (approximate) number of batches to break up the inventory (this many uploaded files)
    """
    batch_size = math.ceil(len(file_name_list) / batches)

    conn = boto3.resource("s3", region_name="us-east-1")
    inventory_bucket_name = f"{main_bucket_name}-inventory"
    conn.create_bucket(Bucket=inventory_bucket_name)

    chunks = [
        file_name_list[x : x + batch_size]
        for x in range(0, len(file_name_list), batch_size)
    ]
    chunk_names = []
    for chunk in chunks:
        mem_file = BytesIO()
        with gzip.GzipFile(fileobj=mem_file, mode="wb") as gz:
            buff = StringIO()
            writer = csv.writer(buff, delimiter=",")
            for test_file_name in chunk:
                writer.writerow([main_bucket_name, test_file_name, 0])
            gz.write(buff.getvalue().encode())
        mem_file.seek(0)
        inventory_fragment_filename = f"{uuid.uuid4()}.csv.gz"
        conn.meta.client.upload_fileobj(
            mem_file, inventory_bucket_name, inventory_fragment_filename
        )
        chunk_names += [
            f"s3://{inventory_bucket_name}/{inventory_fragment_filename}"
        ]
    conn.meta.client.upload_fileobj(
        BytesIO("\n".join(chunk_names).encode()),
        inventory_bucket_name,
        f"{main_bucket_name}/daily-full-inventory/hive/symlink.txt",
    )


# Tests


@pytest.mark.parametrize(
    # Try a number of ranges, partial and whole file downloads
    "initial_range_kb",
    [1, 5, 20, 50, 100, 500],
)
@mock_s3
def test_partial_dicom_download(initial_range_kb):
    """Partial download of DICOM files"""
    # test_file_name = "test_data/sample.dcm"
    test_file_name = str(
        pathlib.Path(__file__).parent.absolute() / "test_data" / "sample.dcm"
    )
    bucket_name = "testbucket-12345"

    # Upload a file to S3
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    conn.meta.client.upload_file(test_file_name, bucket_name, "sample.dcm")
    s3client = S3Client(bucket=bucket_name)

    image_data = PartialDicom(
        s3client, "sample.dcm", initial_range_kb=initial_range_kb
    ).download()

    # Check the local file as if it was fully downloaded
    with open(test_file_name, "rb") as fd:
        tmp = BytesIO(fd.read())
        tmp.seek(0)
        image_data_nonpartial = pydicom.dcmread(tmp, stop_before_pixels=True)

    # Get the list of DICOM tags from both method
    k1 = set(image_data.keys())
    k2 = set(image_data_nonpartial.keys())

    # Compare that the two methods result in the same set of tags
    assert k1 ^ k2 == set()


@mock_s3
def test_patientcache():
    """Test behaviour of the PatientCache for preloading cache
    and looking for hits and misses accordingly.
    """
    test_file_names = [
        f"{TRAINING_PREFIX}data/Covid1/data_2020-09-01.json",
        f"{VALIDATION_PREFIX}data/Covid2/status_2020-09-01.json",
    ]
    main_bucket_name = "testbucket-12345"

    create_inventory(test_file_names, main_bucket_name)

    inv_downloader = InventoryDownloader(main_bucket=main_bucket_name)
    patientcache = PatientCache(inv_downloader)

    # Assert existing ids
    assert patientcache.get_group("Covid1") == "training"
    assert patientcache.get_group("Covid2") == "validation"
    assert patientcache.get_group("Covid3") is None  # Not in cache

    # Assert adding new ids
    new_ids = [("Covid10", "training"), ("Covid11", "validation")]
    for patient_id, group in new_ids:
        assert patientcache.get_group(patient_id) is None
        patientcache.add(patient_id, group)
        assert patientcache.get_group(patient_id) == group

    # Testing cache contradictions
    patient_id = "Covid20"
    patientcache.add(patient_id, "training")
    patientcache.add(
        patient_id, "training"
    )  # adding again to the same group is fine
    with pytest.raises(CacheContradiction, match=rf".* {patient_id}.*"):
        patientcache.add(patient_id, "validation")

    patient_id = "Covid21"
    patientcache.add(patient_id, "validation")
    patientcache.add(
        patient_id, "validation"
    )  # adding again to the same group is fine
    with pytest.raises(CacheContradiction, match=rf".* {patient_id}.*"):
        patientcache.add(patient_id, "training")


@mock_s3
def test_filelist_raw_data():

    target_response = [
        "raw-nhs-upload/2021-01-31/data/Covid1_data.json",
        "raw-nhs-upload/2021-01-31/data/Covid2_status.json",
        "raw-nhs-upload/2021-02-28/data/Covid1_data.json",
        "raw-nhs-upload/2021-02-28/data/Covid2_status.json",
    ]
    other_response = [
        "raw-nhs-upload/2021-02-28/age-0/data/Covid3_status.json",
        f"raw-nhs-upload/2021-02-28/iamge/{pydicom.uid.generate_uid()}.dcm",
        f"{TRAINING_PREFIX}data/Covid1/data_2021-01-31.json",
    ]
    test_file_names = target_response + other_response

    main_bucket_name = "testbucket-12345"

    create_inventory(test_file_names, main_bucket_name)

    inv_downloader = InventoryDownloader(main_bucket=main_bucket_name)
    filelist = FileList(inv_downloader)

    empty_raw_list = list(filelist.get_raw_data_list(raw_prefixes=set()))
    assert len(empty_raw_list) == 0

    acme_raw_list = list(
        filelist.get_raw_data_list(raw_prefixes={"raw-acme-upload"})
    )
    assert len(acme_raw_list) == 0

    nhs_raw_list = sorted(
        filelist.get_raw_data_list(raw_prefixes={"raw-nhs-upload"})
    )

    assert nhs_raw_list == sorted(target_response)


@mock_s3
def test_pending_raw_images_list():

    uuids = [pydicom.uid.generate_uid() for _ in range(4)]

    target_response = [
        f"raw-nhs-upload/2021-01-31/images/{pydicom.uid.generate_uid()}.dcm",
        f"raw-nhs-upload/2021-02-28/images/{pydicom.uid.generate_uid()}.dcm",
        f"raw-nhs-upload/2021-02-28/images/{pydicom.uid.generate_uid()}.dcm",
        f"raw-nhs-upload/2021-02-28/images/{uuids[0]}.dcm",
        f"raw-nhs-upload/2021-02-28/images/{uuids[1]}.dcm",
        f"raw-nhs-upload/2021-02-28/images/{uuids[2]}.dcm",
    ]
    other_response = [
        f"raw-nhs-upload/2021-01-31/age-0/images/{pydicom.uid.generate_uid()}.dcm",
        f"raw-nhs-upload/2021-02-28/age-0/images/{pydicom.uid.generate_uid()}.dcm",
        "raw-nhs-upload/2021-02-28/data/Covid1_data.json",
        "raw-nhs-upload/2021-02-28/data/Covid2_status.json",
        "raw-nhs-upload/2021-02-28/age-0/data/Covid3_status.json",
        f"{TRAINING_PREFIX}data/Covid1/data_2021-02-28.json",
        f"{TRAINING_PREFIX}ct/Covid1/{pydicom.uid.generate_uid()}.dcm",
        f"{TRAINING_PREFIX}mri/Covid1/{pydicom.uid.generate_uid()}.dcm",
        f"{VALIDATION_PREFIX}data/Covid2/status_2020-09-01.json",
        f"{VALIDATION_PREFIX}ct/Covid2/{pydicom.uid.generate_uid()}.dcm",
        f"{VALIDATION_PREFIX}mri/Covid2/{pydicom.uid.generate_uid()}.dcm",
        # Only copied image, so list the relevant image for metadata
        f"{TRAINING_PREFIX}xray/Covid1/123/123/{uuids[1]}.dcm",
        # Only metadata, so list the relevant image
        f"{TRAINING_PREFIX}xray-metadata/Covid2/234/234/{uuids[2]}.json",
        # Skip this as it has both image copy and metadata
        f"raw-nhs-upload/2021-02-28/images/{uuids[3]}.dcm",
        f"{TRAINING_PREFIX}xray/Covid3/345/345/{uuids[3]}.dcm",
        f"{TRAINING_PREFIX}xray-metadata/Covid3/345/345/{uuids[3]}.json",
    ]
    test_file_names = target_response + other_response

    main_bucket_name = "testbucket-12345"

    create_inventory(test_file_names, main_bucket_name, batches=2)

    inv_downloader = InventoryDownloader(main_bucket=main_bucket_name)
    filelist = FileList(inv_downloader)

    empty_pending_list = list(
        filelist.get_pending_raw_images_list(raw_prefixes=set())
    )
    assert len(empty_pending_list) == 0

    acme_pending_list = list(
        filelist.get_pending_raw_images_list(raw_prefixes={"raw-acme-upload"})
    )
    assert len(acme_pending_list) == 0

    nhs_pending_list = sorted(
        filelist.get_pending_raw_images_list(raw_prefixes={"raw-nhs-upload"})
    )

    assert nhs_pending_list == sorted(target_response)


@mock_s3
def test_processed_data_list():

    target_response = [
        f"{TRAINING_PREFIX}data/Covid1/data_2021-02-28.json",
        f"{VALIDATION_PREFIX}data/Covid2/status_2020-09-01.json",
    ]
    other_response = [
        f"{TRAINING_PREFIX}ct/Covid1/{pydicom.uid.generate_uid()}.dcm",
        f"{TRAINING_PREFIX}mri/Covid1/{pydicom.uid.generate_uid()}.dcm",
        f"{VALIDATION_PREFIX}ct/Covid2/{pydicom.uid.generate_uid()}.dcm",
        f"{VALIDATION_PREFIX}mri/Covid2/{pydicom.uid.generate_uid()}.dcm",
        f"raw-nhs-upload/2021-01-31/images/{pydicom.uid.generate_uid()}.dcm",
        f"raw-nhs-upload/2021-02-28/images/{pydicom.uid.generate_uid()}.dcm",
        f"raw-nhs-upload/2021-02-28/images/{pydicom.uid.generate_uid()}.dcm",
        f"raw-nhs-upload/2021-01-31/age-0/images/{pydicom.uid.generate_uid()}.dcm",
        f"raw-nhs-upload/2021-02-28/age-0/images/{pydicom.uid.generate_uid()}.dcm",
        "raw-nhs-upload/2021-02-28/data/Covid1_data.json",
        "raw-nhs-upload/2021-02-28/data/Covid2_status.json",
        "raw-nhs-upload/2021-02-28/age-0/data/Covid3_status.json",
    ]
    test_file_names = target_response + other_response

    main_bucket_name = "testbucket-12345"

    create_inventory(test_file_names, main_bucket_name, batches=2)

    inv_downloader = InventoryDownloader(main_bucket=main_bucket_name)
    filelist = FileList(inv_downloader)

    processed_data = sorted(filelist.get_processed_data_list())

    assert processed_data == sorted(target_response)


@mock_s3
def test_inventory_downloader():

    main_bucket_name = "test-bucket-1234"

    test_file_names = [f"{pydicom.uid.generate_uid()}.dcm" for i in range(100)]
    batches = 10
    create_inventory(test_file_names, main_bucket_name, batches=batches)

    # Check for runtime error
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        inv_downloader = InventoryDownloader(
            main_bucket=main_bucket_name + "-nonexistent"
        )
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1

    inv_downloader = InventoryDownloader(main_bucket=main_bucket_name)

    assert inv_downloader.get_bucket() == main_bucket_name

    all_fragments = [f for f, _ in inv_downloader.get_inventory()]
    assert all_fragments == list(range(batches))

    excludeline = {2, 3, 4}
    some_fragments = [
        f for f, _ in inv_downloader.get_inventory(excludeline=excludeline)
    ]
    assert set(some_fragments) == (set(range(batches)) - excludeline)


@pytest.mark.parametrize(
    "key",
    ["testfile", "path/testfile", "path/subpath/testfile"],
)
@pytest.mark.parametrize("create", [True, False])
@mock_s3
def test_object_exists(key, create):
    """Testing the object_exists function"""

    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    if create:
        conn.meta.client.upload_fileobj(BytesIO(), bucket_name, key)

    # Set up client
    s3client = S3Client(bucket=bucket_name)
    assert s3client.bucket == bucket_name
    assert s3client.object_exists(key) == create


@mock_s3
def test_object_content():
    """Test object_content helper"""
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)

    key = "test.json"
    content = "1234567890"
    conn.meta.client.put_object(Bucket=bucket_name, Key=key, Body=content)

    s3client = S3Client(bucket=bucket_name)
    test_content = s3client.object_content(key).decode("utf-8")
    assert test_content == content

    byte_count = 5
    partial_test_content = s3client.object_content(
        key, content_range=f"bytes=0-{byte_count-1}"
    ).decode("utf-8")
    assert partial_test_content == content[0:byte_count]

    byte_count = len(content) + 5
    oversized_test_content = s3client.object_content(
        key, content_range=f"bytes=0-{byte_count}"
    ).decode("utf-8")
    assert oversized_test_content == content


@mock_s3
def test_get_object():
    """Test get_object helper"""
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)

    key = "test.json"
    content = "1234567890"
    conn.meta.client.put_object(Bucket=bucket_name, Key=key, Body=content)

    s3client = S3Client(bucket=bucket_name)
    test_content = s3client.get_object(key)["Body"].read().decode("utf-8")
    assert test_content == content

    with pytest.raises(ClientError):
        helpers.get_submitting_centre_from_key(s3client, key + ".bak")


@pytest.mark.parametrize(
    "key",
    ["testfile", "path/testfile", "path/subpath/testfile"],
)
@mock_s3
def test_put_object(key):
    """Test object_content helper"""
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)

    content = "1234567890" * 10
    s3client = S3Client(bucket=bucket_name)
    s3client.put_object(key, content=content)
    assert s3client.object_content(key).decode("utf-8") == content


@pytest.mark.parametrize(
    "old_key",
    ["infile.txt", "path/infile.txt", "path/subpath/infile.txt"],
)
@pytest.mark.parametrize(
    "new_key",
    ["outfile.txt", "path/outfile.txt", "path/subpath/outfile.txt"],
)
@mock_s3
def test_copy_object(old_key, new_key):
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)

    content = "1234567890" * 10
    s3client = S3Client(bucket=bucket_name)
    s3client.put_object(old_key, content=content)
    assert not s3client.object_exists(new_key)
    s3client.copy_object(old_key, new_key)
    assert s3client.object_content(old_key).decode(
        "utf-8"
    ) == s3client.object_content(new_key).decode("utf-8")


@mock_s3
def test_upload_file(tmp_path):
    """Test get_object helper"""
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)

    s3client = S3Client(bucket=bucket_name)

    d = tmp_path / "upload"
    d.mkdir()
    p = d / "hello.txt"
    content = "1234567890" * 10
    p.write_text(content)

    # Uploading a test file
    key = "testfile"
    s3client.upload_file(key, str(p))
    assert s3client.object_content(key).decode("utf-8") == content

    # Trying to upload a nonexistent file
    with pytest.raises(FileNotFoundError):
        s3client.upload_file(key, str(d / "nonexistent.txt"))


@mock_s3
def test_get_submitting_centre():
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    s3client = S3Client(bucket=bucket_name)

    key_valid = "valid.json"
    centre = "TestCente"
    content_valid = json.dumps(
        {"Pseudonym": "Covid123", "SubmittingCentre": centre}
    )
    conn.meta.client.put_object(
        Bucket=bucket_name, Key=key_valid, Body=content_valid
    )
    assert (
        helpers.get_submitting_centre_from_key(s3client, key_valid) == centre
    )

    key_missing = "missing.json"
    content_missing = json.dumps({"Pseudonym": "Covid123"})
    conn.meta.client.put_object(
        Bucket=bucket_name, Key=key_missing, Body=content_missing
    )
    assert (
        helpers.get_submitting_centre_from_key(s3client, key_missing) is None
    )

    key_invalid = "invalid.json"
    content_invalid = json.dumps({"Pseudonym": "Covid123"})[:-5]
    conn.meta.client.put_object(
        Bucket=bucket_name, Key=key_invalid, Body=content_invalid
    )

    with pytest.raises(json.decoder.JSONDecodeError):
        helpers.get_submitting_centre_from_key(s3client, key_invalid)

    with pytest.raises(ClientError):
        helpers.get_submitting_centre_from_key(s3client, key_valid + ".bak")


@mock_s3
def test_load_config():
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    s3client = S3Client(bucket=bucket_name)
    config = PipelineConfig()

    input_config = dict(
        {
            "raw_prefixes": [
                "raw-nhs-upload/",
            ],
            "training_percentage": 10,
            "sites": {
                "split": ["Centre1", "Centre2"],
                "training": ["Centre3"],
                "validation": ["Centre4"],
            },
        }
    )
    conn.meta.client.put_object(
        Bucket=bucket_name, Key=CONFIG_KEY, Body=json.dumps(input_config)
    )

    # This function yields, so have to iterate
    next(warehouseloader.load_config(s3client, config))

    assert config.get_raw_prefixes() == set(input_config["raw_prefixes"])
    assert config.get_training_percentage() == 10
    assert config.get_site_group("Centre1") == "split"
    assert config.get_site_group("Centre2") == "split"
    assert config.get_site_group("Centre3") == "training"
    assert config.get_site_group("Centre4") == "validation"
    assert config.get_site_group("CentreX") is None

    # Invalid configuration
    conn.meta.client.put_object(
        Bucket=bucket_name, Key=CONFIG_KEY, Body=json.dumps(input_config)[:-5]
    )
    with pytest.raises(json.decoder.JSONDecodeError):
        # This function yields, so have to iterate
        next(warehouseloader.load_config(s3client, config))


@mock_s3
def test_submittingcentres_extract_raw_data_files():
    """Test the submittingcentres extract_raw_data_files function."""
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    s3client = S3Client(bucket=bucket_name)
    config = PipelineConfig()

    input_config = dict(
        {
            "raw_prefixes": [
                "raw-nhs-upload/",
            ],
            "training_percentage": 0,
            "sites": {
                "split": [],
                "training": [],
                "validation": [],
            },
        }
    )
    conn.meta.client.put_object(
        Bucket=bucket_name, Key=CONFIG_KEY, Body=json.dumps(input_config)
    )
    next(warehouseloader.load_config(s3client, config))

    target_files = [
        "raw-nhs-upload/2021-01-31/data/Covid1_data.json",
        "raw-nhs-upload/2021-01-31/data/Covid2_status.json",
        "raw-nhs-upload/2021-02-28/data/Covid3_data.json",
        "raw-nhs-upload/2021-02-28/data/Covid4_status.json",
    ]
    extra_files = [
        "raw-nhs-upload/2021-03-01/data/Covid1_data.json",
        "test/Covid5_data.json"
        "raw-nhs-upload/age-0/2021-03-01/data/Covid6_data.json",
        "raw-elsewhere-upload/2021-03-01/data/Covid7_data.json",
        "training/data/Covid1/data_2021-01-31.json",
    ]

    create_inventory(target_files + extra_files, bucket_name)

    inv_downloader = InventoryDownloader(main_bucket=bucket_name)
    filelist = FileList(inv_downloader)

    result_list = list(
        submittingcentres.extract_raw_data_files(config, filelist)
    )
    keys_list = sorted([key for _, key, _ in result_list])
    assert keys_list == sorted(target_files)


@mock_s3
def test_submittingcentres_e2e(capsys):
    """Full pipeline run of the submitting centres test:
    * create files
    * add content
    * setup & run pipeline
    """
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    s3client = S3Client(bucket=bucket_name)
    config = PipelineConfig()

    input_config = dict(
        {
            "raw_prefixes": [
                "raw-nhs-upload/",
            ],
            "training_percentage": 0,
            "sites": {
                "split": [],
                "training": [],
                "validation": [],
            },
        }
    )
    conn.meta.client.put_object(
        Bucket=bucket_name, Key=CONFIG_KEY, Body=json.dumps(input_config)
    )
    next(warehouseloader.load_config(s3client, config))

    target_files = [
        "raw-nhs-upload/2021-01-31/data/Covid1_data.json",
        "raw-nhs-upload/2021-01-31/data/Covid2_status.json",
        "raw-nhs-upload/2021-02-28/data/Covid3_data.json",
        "raw-nhs-upload/2021-02-28/data/Covid4_status.json",
    ]
    extra_files = [
        "raw-nhs-upload/2021-03-01/data/Covid1_data.json",
        "test/Covid5_data.json"
        "raw-nhs-upload/age-0/2021-03-01/data/Covid6_data.json",
        "raw-elsewhere-upload/2021-03-01/data/Covid7_data.json",
        "training/data/Covid1/data_2021-01-31.json",
    ]
    centres = ["CentreA", "CentreB", "CentreA", "CentreC"]
    for target_file, centre in zip(target_files, centres):
        file_content = json.dumps({"SubmittingCentre": centre})
        conn.meta.client.put_object(
            Bucket=bucket_name, Key=target_file, Body=file_content
        )

    create_inventory(target_files + extra_files, bucket_name)

    inv_downloader = InventoryDownloader(main_bucket=bucket_name)
    filelist = FileList(inv_downloader)
    services = {
        "config": config,
        "filelist": filelist,
        "s3client": s3client,
    }
    bonobo.run(submittingcentres.get_graph(), services=services)

    with open("/tmp/message.txt", "r") as f:
        output = f.read().splitlines()
    assert output == sorted(list(set(centres)))


##
# Warehouseloader
##


@pytest.mark.parametrize(
    "task",
    ["copy", "else"],
)
@pytest.mark.parametrize(
    "old_key",
    ["infile.txt", "path/subpath/infile.txt"],
)
@pytest.mark.parametrize(
    "new_key",
    ["outfile.txt", "path/subpath/outfile.txt"],
)
@mock_s3
def test_data_copy(task, old_key, new_key):
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    s3client = S3Client(bucket=bucket_name)

    content = "1234567890" * 10
    s3client.put_object(key=old_key, content=content)
    args = task, old_key, new_key
    warehouseloader.data_copy(*args, s3client=s3client)
    if task == "copy":
        assert s3client.object_content(old_key) == s3client.object_content(
            new_key
        )
    else:
        assert not s3client.object_exists(new_key)


@mock_s3
def test_process_patient_data():

    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    s3client = S3Client(bucket=bucket_name)
    config = PipelineConfig()

    input_config = dict(
        {
            "raw_prefixes": [
                "raw-nhs-upload/",
            ],
            "training_percentage": 0,
            "sites": {
                "split": ["SplitCentre"],
                "training": ["TrainingCentre"],
                "validation": ["ValidationCentre"],
            },
        }
    )
    conn.meta.client.put_object(
        Bucket=bucket_name, Key=CONFIG_KEY, Body=json.dumps(input_config)
    )
    next(warehouseloader.load_config(s3client, config))

    processed_list = [
        "training/data/Covid1/data_2021-03-01.json",
        "training/data/Covida9a3751d-f614-4d4a-b3ee-c3f5ca1fb858/data_2021-03-01.json",
        "validation/data/Covid2/data_2021-03-01.json",
        "validation/data/Covida23f28da6-c470-4dd2-b432-1e17724715a2/data_2021-03-01.json",
    ]
    for key in processed_list:
        conn.meta.client.upload_fileobj(BytesIO(), bucket_name, key)

    raw_folder = "raw-nhs-upload/2021-03-01/data"
    clinical_records = [
        ("Covid10", "TrainingCentre"),
        ("Covid20", "ValidationCentre"),
        ("Covid30", "SplitCentre"),
        ("Covid40", "ExtraCentre"),
        ("Covid50", None),
    ]
    data_list = []
    for pseudonym, centre in clinical_records:
        for file_type in ["data", "status"]:
            if centre is not None:
                content = json.dumps(
                    {"Pseudonym": pseudonym, "SubmittingCentre": centre}
                )
            else:
                content = json.dumps({"Pseudonym": pseudonym})

            key = f"{raw_folder}/{pseudonym}_{file_type}.json"
            conn.meta.client.put_object(
                Bucket=bucket_name, Key=key, Body=content
            )
            data_list += [key]

    file_list = processed_list + data_list
    create_inventory(file_list, bucket_name)

    inv_downloader = InventoryDownloader(main_bucket=bucket_name)
    patientcache = PatientCache(inv_downloader)

    kwargs = {
        "config": config,
        "patientcache": patientcache,
        "s3client": s3client,
    }

    # Not handled task
    args = "copy", "raw-nhs-upload/2021-03-01/data/Covid1.json", None
    assert (
        next(warehouseloader.process_patient_data(*args, **kwargs))
        is bonobo.constants.NOT_MODIFIED
    )

    # Not handled filename
    args = (
        "process",
        f"raw-nhs-upload/2021-03-01/images/{pydicom.uid.generate_uid()}.dcm",
        None,
    )
    assert (
        next(warehouseloader.process_patient_data(*args, **kwargs))
        is bonobo.constants.NOT_MODIFIED
    )

    # Already processed file existing
    args = "process", "raw-nhs-upload/2021-03-01/data/Covid1_data.json", None
    with pytest.raises(StopIteration):
        next(warehouseloader.process_patient_data(*args, **kwargs))
    args = "process", "raw-nhs-upload/2021-03-01/data/Covid2_data.json", None
    with pytest.raises(StopIteration):
        next(warehouseloader.process_patient_data(*args, **kwargs))

    # Training item
    args = "process", "raw-nhs-upload/2021-03-01/data/Covid10_data.json", None
    assert next(warehouseloader.process_patient_data(*args, **kwargs)) == (
        "copy",
        "raw-nhs-upload/2021-03-01/data/Covid10_data.json",
        "training/data/Covid10/data_2021-03-01.json",
    )

    # Validation item
    args = (
        "process",
        "raw-nhs-upload/2021-03-01/data/Covid20_status.json",
        None,
    )
    assert next(warehouseloader.process_patient_data(*args, **kwargs)) == (
        "copy",
        "raw-nhs-upload/2021-03-01/data/Covid20_status.json",
        "validation/data/Covid20/status_2021-03-01.json",
    )

    # Split item, training percentage forcing to validation
    args = "process", "raw-nhs-upload/2021-03-01/data/Covid30_data.json", None
    assert next(warehouseloader.process_patient_data(*args, **kwargs)) == (
        "copy",
        "raw-nhs-upload/2021-03-01/data/Covid30_data.json",
        "validation/data/Covid30/data_2021-03-01.json",
    )

    # Unknown submitting centre included
    args = "process", "raw-nhs-upload/2021-03-01/data/Covid40_data.json", None
    with pytest.raises(StopIteration):
        next(warehouseloader.process_patient_data(*args, **kwargs))

    # No submitting centre included
    args = "process", "raw-nhs-upload/2021-03-01/data/Covid50_data.json", None
    with pytest.raises(StopIteration):
        next(warehouseloader.process_patient_data(*args, **kwargs))


@mock_s3
def test_upload_text_data():
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    s3client = S3Client(bucket=bucket_name)

    task = "upload"
    key = "test.txt"
    content = "1234567890" * 10

    ignored_inputs = [
        ("something", key, content),
        (task, None, content),
        (task, key, None),
    ]
    for args in ignored_inputs:
        _, key, _ = args
        assert (
            warehouseloader.upload_text_data(*args, s3client=s3client)
            is bonobo.constants.NOT_MODIFIED
        )
        if key is not None:
            assert not s3client.object_exists(key)

    # Actual upload task
    args = task, key, content
    assert (
        warehouseloader.upload_text_data(*args, s3client=s3client)
        is bonobo.constants.NOT_MODIFIED
    )
    assert s3client.object_content(key).decode("utf-8") == content


@mock_s3
def test_warehouseloader_extract_raw_files():
    """Test the warehouseloader extract_raw_files_from_folder function."""
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    s3client = S3Client(bucket=bucket_name)
    config = PipelineConfig()

    input_config = dict(
        {
            "raw_prefixes": [
                "raw-nhs-upload/",
            ],
            "training_percentage": 0,
            "sites": {
                "split": [],
                "training": [],
                "validation": [],
            },
        }
    )
    conn.meta.client.put_object(
        Bucket=bucket_name, Key=CONFIG_KEY, Body=json.dumps(input_config)
    )
    next(warehouseloader.load_config(s3client, config))

    uuids = [pydicom.uid.generate_uid() for _ in range(4)]

    target_files = [
        "raw-nhs-upload/2021-01-31/data/Covid1_data.json",
        "raw-nhs-upload/2021-01-31/data/Covid2_status.json",
        "raw-nhs-upload/2021-02-28/data/Covid3_data.json",
        "raw-nhs-upload/2021-02-28/data/Covid4_status.json",
        f"raw-nhs-upload/2021-02-28/images/{uuids[0]}.dcm",
        f"raw-nhs-upload/2021-02-28/images/{uuids[1]}.dcm",
        f"raw-nhs-upload/2021-02-28/images/{uuids[2]}.dcm",
    ]
    extra_files = [
        "raw-nhs-upload/2021-03-01/age-0/data/Covid6_data.json",
        f"raw-nhs-upload/2021-02-28/age-0/images/{pydicom.uid.generate_uid()}.dcm",
        "test/Covid5_data.json"
        "raw-elsewhere-upload/2021-03-01/data/Covid7_data.json",
        f"{TRAINING_PREFIX}data/Covid1/data_2021-01-31.json",
        # Only copied image, so list the relevant image for metadata
        f"{TRAINING_PREFIX}xray/Covid1/123/123/{uuids[1]}.dcm",
        # Only metadata, so list the relevant image
        f"{TRAINING_PREFIX}xray-metadata/Covid2/234/234/{uuids[2]}.json",
        # Skip this as it has both image copy and metadata
        f"raw-nhs-upload/2021-02-28/images/{uuids[3]}.dcm",
        f"{TRAINING_PREFIX}xray/Covid3/345/345/{uuids[3]}.dcm",
        f"{TRAINING_PREFIX}xray-metadata/Covid3/345/345/{uuids[3]}.json",
    ]

    create_inventory(target_files + extra_files, bucket_name)

    inv_downloader = InventoryDownloader(main_bucket=bucket_name)
    filelist = FileList(inv_downloader)

    result_list = list(
        warehouseloader.extract_raw_files_from_folder(config, filelist)
    )
    key_set = set([key for _, key, _ in result_list])
    assert key_set ^ set(target_files) == set()


@mock_s3
def test_list_clinical_files():
    """Test the dataprocess list_clinical_files function."""
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)

    target_files = [
        f"{TRAINING_PREFIX}data/Covid1/data_2021-03-01.json",
        f"{TRAINING_PREFIX}data/Covid2/status_2021-03-01.json",
        f"{TRAINING_PREFIX}data/Covid3/data_2021-03-01.json",
        f"{TRAINING_PREFIX}data/Covid3/data_2021-03-05.json",
        f"{TRAINING_PREFIX}data/Covid3/status_2021-03-01.json",
        f"{TRAINING_PREFIX}data/Covid3/status_2021-03-05.json",
        f"{VALIDATION_PREFIX}data/Covid4/data_2021-03-01.json",
        f"{VALIDATION_PREFIX}data/Covid5/status_2021-03-01.json",
        f"{VALIDATION_PREFIX}data/Covid6/data_2021-03-01.json",
        f"{VALIDATION_PREFIX}data/Covid6/data_2021-03-05.json",
        f"{VALIDATION_PREFIX}data/Covid6/status_2021-03-01.json",
        f"{VALIDATION_PREFIX}data/Covid6/status_2021-03-05.json",
    ]
    extra_files = [
        "raw-nhs-upload/2021-03-01/data/Covid6_data.json",
        "raw-nhs-upload/2021-03-06/data/Covid6_data.json",
        f"raw-nhs-upload/2021-02-28/images/{pydicom.uid.generate_uid()}.dcm",
        "test/Covid5_data.json"
        f"{TRAINING_PREFIX}xray/Covid1/{pydicom.uid.generate_uid()}/{pydicom.uid.generate_uid()}/{pydicom.uid.generate_uid()}.dcm",
        f"{TRAINING_PREFIX}xray-metadata/Covid1/{pydicom.uid.generate_uid()}/{pydicom.uid.generate_uid()}/{pydicom.uid.generate_uid()}.json",
        f"{VALIDATION_PREFIX}ct/Covid2/{pydicom.uid.generate_uid()}/{pydicom.uid.generate_uid()}/{pydicom.uid.generate_uid()}.dcm",
        f"{VALIDATION_PREFIX}ct-metadata/Covid2/{pydicom.uid.generate_uid()}/{pydicom.uid.generate_uid()}/{pydicom.uid.generate_uid()}.json",
    ]

    create_inventory(target_files + extra_files, bucket_name)

    inv_downloader = InventoryDownloader(main_bucket=bucket_name)
    filelist = FileList(inv_downloader)

    # Function under test
    results = list(dataprocess.list_clinical_files(filelist))

    assert len(results) == 6

    assert results[0] == (
        "Covid1",
        {"group": "training", "files": ["data_2021-03-01.json"]},
    )

    assert results[1] == (
        "Covid2",
        {"group": "training", "files": ["status_2021-03-01.json"]},
    )

    assert results[2][0] == "Covid3"
    assert results[2][1]["group"] == "training"
    assert sorted(results[2][1]["files"]) == sorted(
        [
            "data_2021-03-01.json",
            "data_2021-03-05.json",
            "status_2021-03-01.json",
            "status_2021-03-05.json",
        ]
    )

    assert results[3] == (
        "Covid4",
        {"group": "validation", "files": ["data_2021-03-01.json"]},
    )

    assert results[4] == (
        "Covid5",
        {"group": "validation", "files": ["status_2021-03-01.json"]},
    )

    assert results[5][0] == "Covid6"
    assert results[5][1]["group"] == "validation"
    assert sorted(results[5][1]["files"]) == sorted(
        [
            "data_2021-03-01.json",
            "data_2021-03-05.json",
            "status_2021-03-01.json",
            "status_2021-03-05.json",
        ]
    )


@mock_s3
def test_list_image_metadata_files():
    """Test the dataprocess list_image_metadata_files function."""
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)

    target_files = [
        f"{TRAINING_PREFIX}xray-metadata/Covid1/1000/2000/3000.json",
        f"{TRAINING_PREFIX}ct-metadata/Covid2/1010/2010/3010.json",
        f"{TRAINING_PREFIX}mri-metadata/Covid3/1020/2020/3020.json",
        f"{VALIDATION_PREFIX}xray-metadata/Covid4/1030/2030/3030.json",
        f"{VALIDATION_PREFIX}ct-metadata/Covid5/1040/2040/3040.json",
        f"{VALIDATION_PREFIX}mri-metadata/Covid6/1050/2050/3050.json",
        # Multiple files per section
        f"{TRAINING_PREFIX}xray-metadata/Covid7/1060/2020/3060.json",
        f"{TRAINING_PREFIX}xray-metadata/Covid7/1060/2020/3061.json",
        f"{TRAINING_PREFIX}xray-metadata/Covid7/1060/2020/3062.json",
        f"{TRAINING_PREFIX}xray-metadata/Covid7/1060/2021/3063.json",
        f"{TRAINING_PREFIX}xray-metadata/Covid7/1060/2021/3064.json",
    ]
    extra_files = [
        f"{TRAINING_PREFIX}xray/Covid1/1000/2000/3000.dcm",
        f"{TRAINING_PREFIX}ct/Covid2/1010/2010/3010.dcm",
        f"{TRAINING_PREFIX}mri/Covid3/1020/2020/3020.dcm",
        f"{VALIDATION_PREFIX}xray/Covid4/1030/2030/3030.dcm",
        f"{VALIDATION_PREFIX}ct/Covid5/1040/2040/3040.dcm",
        f"{VALIDATION_PREFIX}mri/Covid6/1050/2050/3050.dcm",
    ]

    create_inventory(target_files + extra_files, bucket_name)

    inv_downloader = InventoryDownloader(main_bucket=bucket_name)
    filelist = FileList(inv_downloader)

    # Function under test
    results = list(dataprocess.list_image_metadata_files(filelist))

    assert len(results) == 7

    assert ("training", "xray", target_files[0]) in results
    assert ("training", "ct", target_files[1]) in results
    assert ("training", "mri", target_files[2]) in results
    assert ("validation", "xray", target_files[3]) in results
    assert ("validation", "ct", target_files[4]) in results
    assert ("validation", "mri", target_files[5]) in results

    # find the result of multifile
    multi_file_result = [
        item for item in results if item[2] in target_files[6:]
    ][0]
    assert multi_file_result[0] == "training"
    assert multi_file_result[1] == "xray"


@pytest.mark.parametrize(
    "clinical_centre,config_centre,config_group,final_location",
    [
        ("CentreA", "CentreA", "training", "training"),
        ("CentreA", "CentreA", "validation", "validation"),
        ("CentreA", "CentreA", "split", "validation"),
        ("CentreA", "CentreB", "training", None),
    ],
)
@mock_s3
def test_warehouseloader_e2e(
    clinical_centre, config_centre, config_group, final_location
):
    """Full pipeline run of the pipeline test

    Single image file, checking processing and copying going to the right
    place.
    """
    test_file_name = (
        "1.3.6.1.4.1.11129.5.5.110503645592756492463169821050252582267888.dcm"
    )
    test_file_path = str(
        pathlib.Path(__file__).parent.absolute() / "test_data" / test_file_name
    )
    patient_id = "Covid0000"
    study_id = (
        "1.3.6.1.4.1.11129.5.5.112507010803284478207522016832191866964708"
    )
    series_id = (
        "1.3.6.1.4.1.11129.5.5.112630850362182468372440828755218293352329"
    )

    # Test setup
    bucket_name = "testbucket-12345"
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)
    s3client = S3Client(bucket=bucket_name)
    config = PipelineConfig()

    input_config = dict(
        {
            "raw_prefixes": [
                "raw-nhs-upload/",
            ],
            "training_percentage": 0,
            "sites": {
                "split": [],
                "training": [],
                "validation": [],
            },
        }
    )
    input_config["sites"][config_group] += [config_centre]
    conn.meta.client.put_object(
        Bucket=bucket_name, Key=CONFIG_KEY, Body=json.dumps(input_config)
    )
    next(warehouseloader.load_config(s3client, config))

    # Upload the test image
    image_file = f"raw-nhs-upload/2021-03-01/images/{test_file_name}"
    conn.meta.client.upload_file(test_file_path, bucket_name, image_file)

    clinical_files = [
        "raw-nhs-upload/2021-02-15/data/Covid0000_status.json",
        "raw-nhs-upload/2021-03-01/data/Covid0000_data.json",
    ]
    file_content = json.dumps(
        {"Pseudonym": patient_id, "SubmittingCentre": clinical_centre}
    )
    for clinical_file in clinical_files:
        conn.meta.client.put_object(
            Bucket=bucket_name, Key=clinical_file, Body=file_content
        )

    target_files = [image_file] + clinical_files
    create_inventory(target_files, bucket_name)

    inv_downloader = InventoryDownloader(main_bucket=bucket_name)
    filelist = FileList(inv_downloader)
    patientcache = PatientCache(inv_downloader)
    services = {
        "config": config,
        "filelist": filelist,
        "patientcache": patientcache,
        "s3client": s3client,
    }
    bonobo.run(warehouseloader.get_graph(), services=services)

    if final_location is not None:
        # Image copied to the right place
        image_key = f"{final_location}/xray/{patient_id}/{study_id}/{series_id}/{test_file_name}"
        assert s3client.object_exists(image_key)

        # DICOM tags are extracted
        json_key = f"{final_location}/xray-metadata/{patient_id}/{study_id}/{series_id}/{test_file_name.replace('dcm', 'json')}"
        assert s3client.object_exists(json_key)

        with open(test_file_path.replace("dcm", "json"), "r") as f:
            test_json = f.read().replace("\n", "")
        assert s3client.object_content(json_key).decode("utf-8") == test_json

        # Clinical files copied to the right place
        clinical_file_status = (
            f"{final_location}/data/{patient_id}/status_2021-02-15.json"
        )
        assert s3client.object_exists(clinical_file_status)
        clinical_file_data = (
            f"{final_location}/data/{patient_id}/data_2021-03-01.json"
        )
        assert s3client.object_exists(clinical_file_data)
    else:
        for group in ["training", "validation"]:
            image_key = f"{group}/xray/{patient_id}/{study_id}/{series_id}/{test_file_name}"
            assert not s3client.object_exists(image_key)
            json_key = f"{group}/xray-metadata/{patient_id}/{study_id}/{series_id}/{test_file_name.replace('dcm', 'json')}"
            assert not s3client.object_exists(json_key)
            clinical_file_status = (
                f"{group}/data/{patient_id}/status_2021-02-15.json"
            )
            assert not s3client.object_exists(clinical_file_status)
            clinical_file_data = (
                f"{group}/data/{patient_id}/data_2021-03-01.json"
            )
            assert not s3client.object_exists(clinical_file_data)
