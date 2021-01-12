import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from flask_caching import Cache
from pages import tools
from dataset import Dataset
from pages.tools import numformat
import datetime
import pandas as pd

cache = Cache(config={"CACHE_TYPE": "simple"})

RECENT_CUTOFF_DAYS = 30

# Caching is done so that when the dataset's values
# are updated, the page will pull in the updated values.
@cache.cached(timeout=180)
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

    patient = data.data["patient"]

    number_patients = patient["Pseudonym"].nunique()
    pos_patients = set(patient[patient["filename_covid_status"]]["Pseudonym"])
    neg_patients = set(patient[~patient["filename_covid_status"]]["Pseudonym"])
    training_patients = set(patient[patient["group"] == "training"]["Pseudonym"])
    validation_patients = set(patient[patient["group"] == "validation"]["Pseudonym"])

    number_training_patients = len(training_patients)
    number_validation_patients = len(validation_patients)

    number_pos_training_patients = len(training_patients & pos_patients)
    number_pos_validation_patients = len(validation_patients & pos_patients)
    number_pos_patients = number_pos_training_patients + number_pos_validation_patients

    number_neg_training_patients = len(training_patients & neg_patients)
    number_neg_validation_patients = len(validation_patients & neg_patients)
    number_neg_patients = number_neg_training_patients + number_neg_validation_patients

    date_cutoff = datetime.datetime.now() - datetime.timedelta(RECENT_CUTOFF_DAYS)
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

    table_header = [
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
            html.Td(f"New patients added in the last {RECENT_CUTOFF_DAYS} days"),
            html.Td(numformat(recent_patients)),
            html.Td(numformat(recent_training_patients)),
            html.Td(numformat(recent_validation_patients)),
        ]
    )
    table_body = [html.Tbody([row1, row2, row3, row4])]
    table = dbc.Table(
        table_header + table_body,
        bordered=True,
        responsive=True,
    )

    ct = data.data["ct"]
    number_training_ct_studies = ct[ct["group"] == "training"][
        "StudyInstanceUID"
    ].nunique()
    number_validation_ct_studies = ct[ct["group"] == "validation"][
        "StudyInstanceUID"
    ].nunique()
    number_ct_studies = number_training_ct_studies + number_validation_ct_studies
    mri = data.data["mri"]
    number_training_mri_studies = mri[mri["group"] == "training"][
        "StudyInstanceUID"
    ].nunique()
    number_validation_mri_studies = mri[mri["group"] == "validation"][
        "StudyInstanceUID"
    ].nunique()
    number_mri_studies = number_training_mri_studies + number_validation_mri_studies
    xray = data.data["xray"]
    number_training_xray_studies = xray[xray["group"] == "training"][
        "StudyInstanceUID"
    ].nunique()
    number_validation_xray_studies = xray[xray["group"] == "validation"][
        "StudyInstanceUID"
    ].nunique()
    number_xray_studies = number_training_xray_studies + number_validation_xray_studies

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

    table2_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Images"),
                    html.Th("Total"),
                    html.Th("Training"),
                    html.Th("Validation"),
                ]
            ),
            className="thead-dark",
        )
    ]
    image_rows = [
        html.Tr([html.Td(img[0])] + [html.Td(val) for val in img[1]])
        for img in sorted_img_counts
    ]
    table2_body = [html.Tbody(image_rows)]
    table2 = dbc.Table(
        table2_header + table2_body,
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

    table3_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Submitting centres"),
                    html.Th("Total"),
                    html.Th("Training"),
                    html.Th("Validation"),
                ]
            ),
            className="thead-dark",
        )
    ]
    table3_body = [
        html.Tbody(
            [
                html.Tr(
                    [
                        html.Td("Number of submitting centres (e.g. trusts)"),
                        html.Td(numformat(trusts)),
                        html.Td(numformat(training_trusts)),
                        html.Td(numformat(validation_trusts)),
                    ]
                )
            ]
        )
    ]
    table3 = dbc.Table(
        table3_header + table3_body,
        bordered=True,
        responsive=True,
    )

    page = html.Div(
        children=[
            html.H1(children="Summary"),
            html.Div(
                children="""
                    Overview of the high level metrics of the NCCID dataset.
                """
            ),
            table,
            dbc.Alert(
                "Note that patients above count all that have clinical data, whether or not they have images in the dataset yet.",
                color="info",
            ),
            table2,
            table3,
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
    cache.init_app(app.server)

    app.layout = lambda: serve_layout(data)

    return app
