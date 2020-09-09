import csv
import gzip
import pathlib
import re
from io import BytesIO, StringIO

import boto3
import pydicom
import pytest
from moto import mock_s3

import warehouse
from warehouse.components.constants import TRAINING_PREFIX, VALIDATION_PREFIX
from warehouse.components.services import (
    DuplicateKeyError,
    Inventory,
    KeyCache,
    PatientCache,
)
from warehouse.warehouseloader import (
    PartialDicom,
    load_existing_files,
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
    """Known test/validation split values
    """
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
    "training_percentage", [0, 25, 50, 75, 100],
)
def test_training_set_equivalence(
    patient_id, alternate_patient_id, training_percentage
):
    """String transformations should not change validation outcome
    """
    assert warehouse.warehouseloader.patient_in_training_set(
        patient_id, training_percentage
    ) == warehouse.warehouseloader.patient_in_training_set(
        alternate_patient_id, training_percentage
    )


def test_process_dicom_data():
    test_file_name = str(
        pathlib.Path(__file__).parent.absolute() / "test_data" / "sample.dcm"
    )

    test_file_json = test_file_name.replace(".dcm", ".json")
    print(test_file_json)
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
    """Partial download of DICOM files
    """
    # test_file_name = "test_data/sample.dcm"
    test_file_name = str(
        pathlib.Path(__file__).parent.absolute() / "test_data" / "sample.dcm"
    )

    # Upload a file to S3
    conn = boto3.resource("s3", region_name="eu-west-2")
    conn.create_bucket(Bucket="testbucket")
    conn.meta.client.upload_file(test_file_name, "testbucket", "sample.dcm")
    test_object = conn.Object("testbucket", "sample.dcm")
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


def test_keycache():
    """Test behaviour of the KeyCache
    """
    kc = KeyCache()

    kc.add("test1")
    with pytest.raises(DuplicateKeyError):
        kc.add("test1")
    with pytest.raises(DuplicateKeyError):
        kc.add("prefix/test1")

    assert kc.exists(key="test1")
    assert kc.exists(key="prefix/test1")
    assert not kc.exists(key="prefix/test1", fullpath=True)
    assert not kc.exists(key="test")


@mock_s3
def test_load_existing_files():
    """Test loading existing files with an Inventory, to ensure
    we have the same results as directly listing the bucket.
    """

    test_file_names = [
        f"{TRAINING_PREFIX}data/Covid1/data_2020-09-01.json",
        f"{TRAINING_PREFIX}ct/Covid1/{pydicom.uid.generate_uid()}.dcm",
        f"{TRAINING_PREFIX}mri/Covid1/{pydicom.uid.generate_uid()}.dcm",
        f"{VALIDATION_PREFIX}data/Covid2/status_2020-09-01.json",
        f"{VALIDATION_PREFIX}ct/Covid2/{pydicom.uid.generate_uid()}.dcm",
        f"{VALIDATION_PREFIX}mri/Covid2/{pydicom.uid.generate_uid()}.dcm",
    ]

    conn = boto3.resource("s3", region_name="eu-west-2")

    main_bucket_name = "testbucket"
    conn.create_bucket(Bucket=main_bucket_name)

    for test_file_name in test_file_names:
        conn.meta.client.upload_fileobj(
            BytesIO(), main_bucket_name, test_file_name
        )

    inventory_bucket_name = f"{main_bucket_name}-inventory"
    conn.create_bucket(Bucket=inventory_bucket_name)

    mem_file = BytesIO()
    with gzip.GzipFile(fileobj=mem_file, mode="wb") as gz:
        buff = StringIO()
        writer = csv.writer(buff, delimiter=",")
        for test_file_name in test_file_names:
            writer.writerow([main_bucket_name, test_file_name, 0])
        gz.write(buff.getvalue().encode())
    mem_file.seek(0)
    conn.meta.client.upload_fileobj(
        mem_file, inventory_bucket_name, "inventory.csv.gz"
    )
    conn.meta.client.upload_fileobj(
        BytesIO(f"s3://{inventory_bucket_name}/inventory.csv.gz".encode()),
        inventory_bucket_name,
        f"{main_bucket_name}/daily-full-inventory/hive/symlink.txt",
    )

    keycache = KeyCache()
    patientcache = PatientCache()
    inventory = Inventory(main_bucket=main_bucket_name)

    load_existing_files(keycache, patientcache, inventory)

    patient_file_name = re.compile(
        r"^(?P<group>.*)/data/(?P<patient_id>.*)/(?:data|status)_\d{4}-\d{2}-\d{2}.json$"
    )

    for test_file_name in test_file_names:
        m = patient_file_name.match(test_file_name)
        if m:
            # It is a patient file
            assert patientcache.get_group(m.group("patient_id")) == m.group(
                "group"
            )
        else:
            # It is an image file
            assert keycache.exists(test_file_name, fullpath=True)
