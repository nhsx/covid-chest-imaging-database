import datetime

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd

from dataset import Dataset
from pages import tools
from pages.tools import numformat, storage_format, show_last_update

RECENT_CUTOFF_DAYS = 30


def serve_layout(data: Dataset) -> html.Div:
    """Create the page layout for the summary page

    Parameters
    ----------
    data : dataset.Dataset
        The main dataset which is used for analysis.

    Returns
    -------
    dash_html_components.Div
        The HTML componets of the page layout, wrapped in  div
    """

    patient = data.dataset("patient")

    number_patients = patient["Pseudonym"].nunique()
    pos_patients = set(patient[patient["filename_covid_status"]]["Pseudonym"])
    neg_patients = set(patient[~patient["filename_covid_status"]]["Pseudonym"])
    training_patients = set(
        patient[patient["group"] == "training"]["Pseudonym"]
    )
    validation_patients = set(
        patient[patient["group"] == "validation"]["Pseudonym"]
    )

    number_training_patients = len(training_patients)
    number_validation_patients = len(validation_patients)

    number_pos_training_patients = len(training_patients & pos_patients)
    number_pos_validation_patients = len(validation_patients & pos_patients)
    number_pos_patients = (
        number_pos_training_patients + number_pos_validation_patients
    )

    number_neg_training_patients = len(training_patients & neg_patients)
    number_neg_validation_patients = len(validation_patients & neg_patients)
    number_neg_patients = (
        number_neg_training_patients + number_neg_validation_patients
    )

    date_cutoff = datetime.datetime.now() - datetime.timedelta(
        RECENT_CUTOFF_DAYS
    )
    recent_training_patients = sum(
        pd.to_datetime(
            patient[patient["group"] == "training"]["filename_earliest_date"]
        )
        >= date_cutoff
    )
    recent_validation_patients = sum(
        pd.to_datetime(
            patient[patient["group"] == "validation"]["filename_earliest_date"]
        )
        >= date_cutoff
    )
    recent_patients = recent_training_patients + recent_validation_patients

    table_patient_count_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Patients"),
                    html.Th("Total"),
                    html.Th("Training"),
                    html.Th("Validation"),
                ]
            ),
            className="thead-dark",
        )
    ]
    row1 = html.Tr(
        [
            html.Td("Total number of patients"),
            html.Td(numformat(number_patients)),
            html.Td(numformat(number_training_patients)),
            html.Td(numformat(number_validation_patients)),
        ]
    )
    row2 = html.Tr(
        [
            html.Td("Total number of positive patients"),
            html.Td(numformat(number_pos_patients)),
            html.Td(numformat(number_pos_training_patients)),
            html.Td(numformat(number_pos_validation_patients)),
        ]
    )
    row3 = html.Tr(
        [
            html.Td("Total number of negative patients"),
            html.Td(numformat(number_neg_patients)),
            html.Td(numformat(number_neg_training_patients)),
            html.Td(numformat(number_neg_validation_patients)),
        ]
    )
    row4 = html.Tr(
        [
            html.Td(
                f"New patients added in the last {RECENT_CUTOFF_DAYS} days"
            ),
            html.Td(numformat(recent_patients)),
            html.Td(numformat(recent_training_patients)),
            html.Td(numformat(recent_validation_patients)),
        ]
    )
    table_patient_count_body = [html.Tbody([row1, row2, row3, row4])]
    table_patient_count = dbc.Table(
        table_patient_count_header + table_patient_count_body,
        bordered=True,
        responsive=True,
    )

    ct = data.dataset("ct")
    number_training_ct_studies = ct[ct["group"] == "training"][
        "StudyInstanceUID"
    ].nunique()
    number_validation_ct_studies = ct[ct["group"] == "validation"][
        "StudyInstanceUID"
    ].nunique()
    number_ct_studies = (
        number_training_ct_studies + number_validation_ct_studies
    )
    mri = data.dataset("mri")
    number_training_mri_studies = mri[mri["group"] == "training"][
        "StudyInstanceUID"
    ].nunique()
    number_validation_mri_studies = mri[mri["group"] == "validation"][
        "StudyInstanceUID"
    ].nunique()
    number_mri_studies = (
        number_training_mri_studies + number_validation_mri_studies
    )
    xray = data.dataset("xray")
    number_training_xray_studies = xray[xray["group"] == "training"][
        "StudyInstanceUID"
    ].nunique()
    number_validation_xray_studies = xray[xray["group"] == "validation"][
        "StudyInstanceUID"
    ].nunique()
    number_xray_studies = (
        number_training_xray_studies + number_validation_xray_studies
    )

    img_counts = {
        "CT image studies": [
            number_ct_studies,
            number_training_ct_studies,
            number_validation_ct_studies,
        ],
        "MRI image studies": [
            number_mri_studies,
            number_training_mri_studies,
            number_validation_mri_studies,
        ],
        "X-ray image studies": [
            number_xray_studies,
            number_training_xray_studies,
            number_validation_xray_studies,
        ],
    }

    sorted_img_counts = list(
        map(
            lambda item: [item[0], [numformat(val) for val in item[1]]],
            sorted(
                [[item, img_counts[item]] for item in img_counts],
                key=lambda item: item[1][0],
                reverse=True,
            ),
        )
    )

    table_img_counts_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Image Counts"),
                    html.Th("Total"),
                    html.Th("Training"),
                    html.Th("Validation"),
                ]
            ),
            className="thead-dark",
        )
    ]

    def sum_image_counts(col=0):
        """Get sums of image counts actoss modalities for each set"""
        return sum([v[col] for v in img_counts.values()])

    image_rows = [
        html.Tr(
            [
                html.Td("Across all modalities"),
                html.Td(numformat(sum_image_counts(0))),
                html.Td(numformat(sum_image_counts(1))),
                html.Td(numformat(sum_image_counts(2))),
            ]
        ),
    ]
    image_rows += [
        html.Tr([html.Td(img[0])] + [html.Td(val) for val in img[1]])
        for img in sorted_img_counts
    ]
    table_img_counts_body = [html.Tbody(image_rows)]
    table_img_counts = dbc.Table(
        table_img_counts_header + table_img_counts_body,
        bordered=True,
        responsive=True,
    )

    storage = data.dataset("storage")

    ct_training_storage = storage[storage["prefix"] == "training/ct/"][
        "storage"
    ].values[0]
    ct_validation_storage = storage[storage["prefix"] == "validation/ct/"][
        "storage"
    ].values[0]
    ct_total_storage = ct_training_storage + ct_validation_storage

    mri_training_storage = storage[storage["prefix"] == "training/mri/"][
        "storage"
    ].values[0]
    mri_validation_storage = storage[storage["prefix"] == "validation/mri/"][
        "storage"
    ].values[0]
    mri_total_storage = mri_training_storage + mri_validation_storage

    xray_training_storage = storage[storage["prefix"] == "training/xray/"][
        "storage"
    ].values[0]
    xray_validation_storage = storage[storage["prefix"] == "validation/xray/"][
        "storage"
    ].values[0]
    xray_total_storage = xray_training_storage + xray_validation_storage

    total_training_storage = storage[storage["prefix"] == "training/"][
        "storage"
    ].values[0]
    total_validation_storage = storage[storage["prefix"] == "validation/"][
        "storage"
    ].values[0]
    total_storage = total_training_storage + total_validation_storage

    metadata_training_storage = total_training_storage - (
        ct_training_storage + mri_training_storage + xray_training_storage
    )
    metadata_validation_storage = total_validation_storage - (
        ct_validation_storage
        + mri_validation_storage
        + xray_validation_storage
    )
    metadata_total_storage = (
        metadata_training_storage + metadata_validation_storage
    )

    table_img_storage_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Image Storage"),
                    html.Th("Total"),
                    html.Th("Training"),
                    html.Th("Validation"),
                ]
            ),
            className="thead-dark",
        )
    ]

    img_storage_dict = {
        "CT image storage": [
            ct_total_storage,
            ct_training_storage,
            ct_validation_storage,
        ],
        "MRI image storage": [
            mri_total_storage,
            mri_training_storage,
            mri_validation_storage,
        ],
        "X-ray image storage": [
            xray_total_storage,
            xray_training_storage,
            xray_validation_storage,
        ],
        "Image metadata and clinical data storage": [
            metadata_total_storage,
            metadata_training_storage,
            metadata_validation_storage,
        ],
    }

    # Order rows by descending value of total storage column
    modalities = img_storage_dict.keys()
    ordered_modalities = sorted(
        modalities, key=lambda x: img_storage_dict[x][0], reverse=True
    )

    image_storage_rows = [
        html.Tr(
            [
                html.Td(
                    "Total image, image metadata, and clinical data storage"
                ),
                html.Td(storage_format(total_storage)),
                html.Td(storage_format(total_training_storage)),
                html.Td(storage_format(total_validation_storage)),
            ]
        ),
    ]

    image_storage_rows += [
        html.Tr(
            [
                html.Td(mod),
                html.Td(storage_format(img_storage_dict[mod][0])),
                html.Td(storage_format(img_storage_dict[mod][1])),
                html.Td(storage_format(img_storage_dict[mod][2])),
            ]
        )
        for mod in ordered_modalities
    ]

    table_img_storage_body = [html.Tbody(image_storage_rows)]

    table_img_storage = dbc.Table(
        table_img_storage_header + table_img_storage_body,
        bordered=True,
        responsive=True,
    )

    trusts = len(set(patient["SubmittingCentre"]))
    training_trusts = len(
        set(patient[patient["group"] == "training"]["SubmittingCentre"])
    )
    validation_trusts = len(
        set(patient[patient["group"] == "validation"]["SubmittingCentre"])
    )

    table_trust_count_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Submitting centres"),
                    html.Th("Total"),
                ]
            ),
            className="thead-dark",
        )
    ]
    table_trust_count_body = [
        html.Tbody(
            [
                html.Tr(
                    [
                        html.Td("Number of submitting centres (e.g. trusts)"),
                        html.Td(numformat(trusts)),
                    ]
                )
            ]
        )
    ]
    table_trust_count = dbc.Table(
        table_trust_count_header + table_trust_count_body,
        bordered=True,
        responsive=True,
    )

    page = html.Div(
        children=[
            html.H1(children="Summary"),
            html.Div(
                html.H3(
                    children="""
                    An overview of the NCCID dataset showing high level metrics
                """
                )
            ),
            html.Div(
                html.P(
                    children="""
                    The National COVID-19 Chest Imaging Database (NCCID) comprises chest X-ray,
                    CT and MR images and other relevant information of patients with suspected COVID-19. 
                    The database has been created to enable the development and validation of automated 
                    analysis technologies that may prove effective in supporting COVID-19 care pathways, 
                    and to accelerate research projects to better understand the disease.
                """
                )
            ),
            table_patient_count,
            dbc.Alert(
                "Note that the patient counts above include all patients with clinical data,"
                " whether or not their imaging data has been provided yet.",
                color="info",
            ),
            table_img_counts,
            table_img_storage,
            table_trust_count,
            show_last_update(data),
        ]
    )
    return page


def create_app(data: Dataset, **kwargs: str) -> dash.Dash:
    """Create a Dash app for the given page

    Parameters
    ----------
    data : dataset.Dataset
        Description of parameter `x`.
    **kwargs : dict
        Keyword arguments to pass on to the Dash app constructor.

    Returns
    -------
    dash.Dash
        The Dash app to display on the given page.
    """
    app = dash.Dash(__name__, **kwargs)

    app.layout = lambda: serve_layout(data)

    return app
