import pathlib

import pydicom
import pytest

import warehouse.components.constants as constants
import warehouse.components.helpers as helpers
import warehouse.components.services as services
from warehouse.dataprocess import dicom_age_in_years
from warehouse.warehouseloader import (
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


@pytest.mark.parametrize(
    "input_file",
    [
        "sample.dcm",
        "1.3.6.1.4.1.11129.5.5.110503645592756492463169821050252582267888.dcm",
    ],
)
def test_process_dicom_data(input_file):
    test_file_name = str(
        pathlib.Path(__file__).parent.absolute() / "test_data" / input_file
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
    assert helpers.get_date_from_key(key) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("", None),
        ("111Y", 111.0),
        ("023Y", 23.0),
        ("002Y", 2.0),
        ("024M", 2.0),
        ("026W", 0.5),
        ("073D", 0.2),
        ("XXXX", None),
        ("XXXY", None),
    ],
)
def test_dicom_age_in_years(value, expected):
    assert dicom_age_in_years(value) == pytest.approx(expected)


@pytest.mark.parametrize(
    "value,expected",
    [
        (-10, 0),
        (50, 50),
        (150, 100),
        (None, constants.TRAINING_PERCENTAGE),
        (34.4, 34.4),
    ],
)
def test_pipeline_config_training_percent(value, expected):
    """
    WHEN various values of training percentage is set
    THEN the results are correctly clipped and filled in from default.
    """
    input_config = dict(
        {
            "raw_prefixes": [],
            "sites": {"split": [], "training": [], "validation": []},
        }
    )
    if value is not None:
        input_config["training_percentage"] = value

    pipelineconfig = services.PipelineConfig()
    pipelineconfig.set_config(input_config)

    assert pipelineconfig.get_training_percentage() == pytest.approx(expected)
