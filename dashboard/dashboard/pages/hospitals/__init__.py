import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from flask_caching import Cache

from dataset import Dataset
from pages.tools import numformat

cache = Cache(config={"CACHE_TYPE": "simple"})


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

    centres = sorted(patient["SubmittingCentre"].unique())
    centres_select = dcc.Dropdown(
        placeholder="Select a submitting site / centre to filter",
        options=[{"label": centre, "value": centre} for centre in centres],
        id="hospital-filter",
    )

    covid_status_select = dcc.Dropdown(
        options=[
            {"label": "All patients", "value": "all"},
            {"label": "Positive patients", "value": "positive"},
            {"label": "Negative patients", "value": "negative"},
        ],
        value="all",
        clearable=False,
        id="covid-status",
    )

    table_order_select = dcc.Dropdown(
        options=[
            {
                "label": "Submitting Centre/Site",
                "value": "Submitting Centre/Site",
            },
            {"label": "First Submission", "value": "First Submission"},
            {"label": "Patients", "value": "Patients"},
            {"label": "Image Studies", "value": "Image Studies"},
        ],
        value="Submitting Centre/Site",
        clearable=False,
        id="table-order",
    )

    selector = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Label(
                                    [
                                        "Select COVID-19 status to filter the data below.",
                                    ],
                                    htmlFor="hospital-filter",
                                ),
                                covid_status_select,
                            ]
                        ),
                        md=6,
                        sm=12,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.Label(
                                    [
                                        "Select table ordering column.",
                                    ],
                                    htmlFor="table-order",
                                ),
                                table_order_select,
                            ]
                        ),
                        md=6,
                        sm=12,
                    ),
                ]
            )
        ]
    )

    page = html.Div(
        children=[
            html.H1(children="Hospital Sites"),
            selector,
            # html.Div(
            #     [
            #         html.Label(
            #             [
            #                 "Select COVID-19 status to filter the data below.",
            #             ],
            #             htmlFor="hospital-filter",
            #         ),
            #         covid_status_select,
            #         html.Label(
            #             [
            #                 "Select table ordering column.",
            #             ],
            #             htmlFor="table-order",
            #         ),
            #         table_order_select,
            #     ]
            # ),
            html.Br(),
            html.Div(id="hospital-table"),
            html.Br(),
            html.Div(id="hospital-datatable"),
            html.Br(),
            html.Label(
                [
                    "Select Submitting Centre/Site to filter below",
                ],
                htmlFor="hospital-filter",
            ),
            centres_select,
            html.Div(id="patients-swabs"),
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

    @app.callback(
        Output("hospital-table", "children"),
        Input("covid-status", "value"),
        Input("table-order", "value"),
    )
    def set_hostpital_table(covid_status, order_column):
        return create_hospital_table(data, covid_status, order_column)

    @app.callback(
        Output("hospital-datatable", "children"),
        [Input("covid-status", "value")],
    )
    def set_hostpital_datatable(value):
        return create_hospital_datatable(data, value)

    @app.callback(
        Output("patients-swabs", "children"),
        [Input("hospital-filter", "value")],
    )
    def set_hospital_swabs(value):
        return create_hospital_swabs(data, value)

    return app


def create_hospital_table(data, covid_status, order_column):
    patient = data.data["patient"]
    if covid_status == "positive":
        patient = patient[patient["filename_covid_status"]]
    elif covid_status == "negative":
        patient = patient[~patient["filename_covid_status"]]

    ct = data.data["ct"]
    mri = data.data["mri"]
    xray = data.data["xray"]

    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Submitting Centre/Site"),
                    html.Th("First submission"),
                    html.Th("Patients"),
                    html.Th("Image Studies"),
                ]
            ),
            className="thead-dark",
        )
    ]

    submitting_centres = sorted(patient["SubmittingCentre"].unique())
    earliest_dates = []
    patient_counts = []
    study_counts = []
    for centre in submitting_centres:
        patient_ids = set(
            patient[patient["SubmittingCentre"] == centre]["Pseudonym"]
        )
        patient_counts += [len(patient_ids)]
        ct_studies = ct[ct["Pseudonym"].isin(patient_ids)][
            "StudyInstanceUID"
        ].nunique()
        mri_studies = mri[mri["Pseudonym"].isin(patient_ids)][
            "StudyInstanceUID"
        ].nunique()
        xray_studies = xray[xray["Pseudonym"].isin(patient_ids)][
            "StudyInstanceUID"
        ].nunique()
        study_counts += [ct_studies + mri_studies + xray_studies]

        earliest = patient[patient["SubmittingCentre"] == centre][
            "filename_earliest_date"
        ].min()
        earliest_dates += [earliest]

    d = {
        "Submitting Centre/Site": submitting_centres,
        "First Submission": earliest_dates,
        "Patients": patient_counts,
        "Image Studies": study_counts,
    }
    df = pd.DataFrame(data=d)
    df_sorted = df.sort_values(by=[order_column], ascending=False)

    rows = []
    for index, row in df_sorted.iterrows():
        rows += [
            html.Tr(
                [
                    html.Td(row["Submitting Centre/Site"]),
                    html.Td(row["First Submission"]),
                    html.Td(
                        numformat(row["Patients"]), className="text-right"
                    ),
                    html.Td(
                        numformat(row["Image Studies"]), className="text-right"
                    ),
                ]
            )
        ]

    table_body = [html.Tbody(rows)]
    table = dbc.Table(table_header + table_body, bordered=True)

    return table


def create_hospital_datatable(data, covid_status):
    patient = data.data["patient"]
    if covid_status == "positive":
        patient = patient[patient["filename_covid_status"]]
    elif covid_status == "negative":
        patient = patient[~patient["filename_covid_status"]]

    ct = data.data["ct"]
    mri = data.data["mri"]
    xray = data.data["xray"]

    submitting_centres = sorted(patient["SubmittingCentre"].unique())
    earliest_dates = []
    patient_counts = []
    study_counts = []
    for centre in submitting_centres:
        patient_ids = set(
            patient[patient["SubmittingCentre"] == centre]["Pseudonym"]
        )
        patient_counts += [len(patient_ids)]
        ct_studies = ct[ct["Pseudonym"].isin(patient_ids)][
            "StudyInstanceUID"
        ].nunique()
        mri_studies = mri[mri["Pseudonym"].isin(patient_ids)][
            "StudyInstanceUID"
        ].nunique()
        xray_studies = xray[xray["Pseudonym"].isin(patient_ids)][
            "StudyInstanceUID"
        ].nunique()
        study_counts += [ct_studies + mri_studies + xray_studies]

        earliest = patient[patient["SubmittingCentre"] == centre][
            "filename_earliest_date"
        ].min()
        earliest_dates += [earliest]

    d = {
        "Submitting Centres/Sites": submitting_centres,
        "First Submission": earliest_dates,
        "Patients": patient_counts,
        "Image Studies": study_counts,
    }
    df = pd.DataFrame(data=d)
    table = dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        sort_action="native",
    )

    return table


def create_hospital_swabs(data, centre):
    if centre is None:
        title_filter = "All Submitting Centres"
        patients = data.data["patient"].copy()
    else:
        patients = data.data["patient"][
            data.data["patient"]["SubmittingCentre"] == centre
        ]
        title_filter = centre

    # patients["latest_swab_date"] = pd.to_datetime(patients["latest_swab_date"])

    x = (
        patients.groupby(["latest_swab_date"])
        .count()
        .sort_index()["Pseudonym"]
        .cumsum()
        .sort_index()
        .fillna(method="ffill")
    )

    fig = go.Figure(
        data=[go.Scatter(x=x.index, y=x)],
        layout={
            "title": f"Cumulative Number of Patients Swab-Tested: {title_filter}"
        },
    )
    graph = dcc.Graph(id="example-graph", figure=fig)
    return graph
