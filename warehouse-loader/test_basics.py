import pydicom
import pytest

import warehouseloader as wl


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
    assert wl.patient_in_training_set(patient_id, training_percentage) == expected


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
    assert wl.patient_in_training_set(
        patient_id, training_percentage
    ) == wl.patient_in_training_set(alternate_patient_id, training_percentage)


@pytest.mark.parametrize(
    "key, expected",
    [
        ("raw/2020-04-30/test.json", "2020-04-30"),
        ("raw/2020-5-5/test.json", None),
        ("raw/another/2020-04-30/test.json", "2020-04-30"),
        ("2020-04-30/test.json", None),
        ("anywhere/0000-00-00/anything", "0000-00-00"),
    ],
)
def test_get_date_from_key(key, expected):
    assert wl.get_date_from_key(key) == expected


@pytest.mark.parametrize(
    "cache,key,expected",
    [
        ({}, "data_2020-04-30.json", "2020-04-30"),
        ({}, "status_2020-04-30.json", "2020-04-30"),
        ({}, "example_2020-04-30.json", "2020-04-30"),
        ({"test.dcm": "2020-04-30"}, "test.json", "2020-04-30"),
        ({"test.dcm": "2020-04-30"}, "TEST.JSON", "2020-04-30"),
        ({}, "test.json", None),
        ({"test.dcm": "2020-04-30"}, "test.dcm", "2020-04-30"),
        ({"test.dcm": "2020-04-30"}, "TEST.DCM", "2020-04-30"),
        ({}, "test.dcm", None),
    ],
)
def test_get_summary_date(cache, key, expected):
    assert wl.get_summary_date(cache, key) == expected


def test_process_dicom_data():
    test_file_name = "test_data/sample.dcm"
    test_file_json = test_file_name.replace(".dcm", ".json")
    print(test_file_json)
    image_data = pydicom.dcmread(test_file_name, stop_before_pixels=True)
    task, metadata_key, processed_image_data = next(
        wl.process_dicom_data("metadata", test_file_name, image_data)
    )
    assert task == "upload"
    assert metadata_key == test_file_name
    with open(test_file_json, "r") as f:
        test_json = f.read().replace("\n", "")
    assert test_json == processed_image_data
