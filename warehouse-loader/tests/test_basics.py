import csv
import gzip
import math
import os
import pathlib
import uuid
from io import BytesIO, StringIO

import boto3
import pydicom
import pytest
from moto import mock_s3

import warehouse.components.helpers as helpers
from warehouse.components.constants import TRAINING_PREFIX, VALIDATION_PREFIX
from warehouse.components.services import (
    CacheContradiction,
    FileList,
    InventoryDownloader,
    PatientCache,
    S3Client,
)
from warehouse.warehouseloader import (
    PartialDicom,
    get_date_from_key,
    patient_in_training_set,
    process_dicom_data,
)


@pytest.mark.parametrize(
    "patient_id,training_percentage,expected",
    [
        ("Covid1", 0, False),
        ("Covid1", 100, True),
        ("Covid1", 50, True),
        ("Covid14", 50, False),
        ("Covid20", 50, True),
        ("Covid149", 50, False),
    ],
)
def test_training_set_basics(patient_id, training_percentage, expected):
    """Known test/validation split values"""
    assert patient_in_training_set(patient_id, training_percentage) == expected


@pytest.mark.parametrize(
    "patient_id,alternate_patient_id",
    [
        ("Covid1", "COVID1"),
        ("covid1", "coviD1"),
        ("CoViD1", "cOvId1"),
        (" covid1", "covid1"),
        ("covid1", "covid1 "),
    ],
)
@pytest.mark.parametrize(
    "training_percentage",
    [0, 25, 50, 75, 100],
)
def test_training_set_equivalence(
    patient_id, alternate_patient_id, training_percentage
):
    """String transformations should not change validation outcome"""
    assert patient_in_training_set(
        patient_id, training_percentage
    ) == patient_in_training_set(alternate_patient_id, training_percentage)


def test_process_dicom_data():
    test_file_name = str(
        pathlib.Path(__file__).parent.absolute() / "test_data" / "sample.dcm"
    )

    test_file_json = test_file_name.replace(".dcm", ".json")
    image_data = pydicom.dcmread(test_file_name, stop_before_pixels=True)
    task, metadata_key, processed_image_data = next(
        process_dicom_data("metadata", test_file_name, image_data)
    )
    assert task == "upload"
    assert metadata_key == test_file_name
    with open(test_file_json, "r") as f:
        test_json = f.read().replace("\n", "")
    assert test_json == processed_image_data


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
    test_object = conn.Object(bucket_name, "sample.dcm")
    image_data = PartialDicom(
        test_object, initial_range_kb=initial_range_kb
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
        [
            obj.key
            for obj in filelist.get_raw_data_list(
                raw_prefixes={"raw-nhs-upload"}
            )
        ]
    )

    assert nhs_raw_list == sorted(target_response)


@mock_s3
def test_pending_raw_images_list():

    target_response = [
        f"raw-nhs-upload/2021-01-31/images/{pydicom.uid.generate_uid()}.dcm",
        f"raw-nhs-upload/2021-02-28/images/{pydicom.uid.generate_uid()}.dcm",
        f"raw-nhs-upload/2021-02-28/images/{pydicom.uid.generate_uid()}.dcm",
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
        [
            obj.key
            for obj in filelist.get_pending_raw_images_list(
                raw_prefixes={"raw-nhs-upload"}
            )
        ]
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

    processed_data = sorted(
        [obj.key for obj in filelist.get_processed_data_list()]
    )

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
    assert (
        helpers.object_exists(s3client.client, s3client.bucket, key) == create
    )


@pytest.mark.parametrize(
    "key,expected",
    [
        ("", None),
        ("file", None),
        ("path/subpath/file", None),
        ("2021-01-01", None),
        ("path/2021-01-01", None),
        ("path/2021-01-01/file", "2021-01-01"),
        ("path/subpath/2021-01-01/file", "2021-01-01"),
        ("path/subpath/2021-01-01/subsubpath/file", "2021-01-01"),
        ("path/2021-12-12/file", "2021-12-12"),
    ],
)
def test_get_date_from_key(key, expected):
    assert get_date_from_key(key) == expected
