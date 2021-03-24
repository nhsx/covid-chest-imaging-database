import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from jinja2 import utils

from dataset import Dataset
from pages.tools import show_last_update


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
            {"label": "Latest Submission", "value": "Latest Submission"},
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
                                    htmlFor="covid-status",
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
                                        "Select field to sort rows by.",
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
            html.H2("Sites Overview"),
            selector,
            html.Br(),
            dcc.Loading(
                id="loading-hospital-table",
                type="dot",
                color="black",
                children=html.Div(id="hospital-table"),
            ),
            html.Hr(),
            html.H2("Data Over Time"),
            html.Label(
                [
                    "Select Submitting Centre/Site to filter above",
                ],
                htmlFor="hospital-filter",
            ),
            centres_select,
            html.P(
                "ⓘ Click the × mark to clear the selection above and show data for all submitting centres.",
                id="centres-note",
            ),
            dcc.Loading(
                id="loading-patients-swabs",
                type="dot",
                color="black",
                children=html.Div(id="patients-swabs"),
            ),
            dbc.Alert(
                "ⓘ Data collection for the NCCID began in May 2020 "
                + " but includes patients admitted to hospital since Februray 2020.",
                color="info",
            ),
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

    @app.callback(
        Output("hospital-table", "children"),
        Input("covid-status", "value"),
        Input("table-order", "value"),
    )
    def set_hostpital_table(covid_status, order_column):
        return create_hospital_table(data, covid_status, order_column)

    @app.callback(
        Output("patients-swabs", "children"),
        Input("hospital-filter", "value"),
    )
    def set_hospital_counts(centre):
        return create_hospital_counts(data, centre)

    @app.callback(
        Output("centres-note", "className"),
        Input("hospital-filter", "value"),
    )
    def toggle_centres_note_visibility(centre):
        return "invisible" if centre is None else "visible"

    return app


def create_hospital_table(data, covid_status, order_column):
    patient = data.dataset("patient")
    if covid_status == "positive":
        patient = patient[patient["filename_covid_status"]]
    elif covid_status == "negative":
        patient = patient[~patient["filename_covid_status"]]

    ct = data.dataset("ct")
    mri = data.dataset("mri")
    xray = data.dataset("xray")

    submitting_centres = sorted(patient["SubmittingCentre"].unique())
    earliest_dates = []
    latest_dates = []
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

        latest = patient[patient["SubmittingCentre"] == centre][
            "filename_latest_date"
        ].max()
        latest_dates += [latest]
    d = {
        "Submitting Centre/Site": submitting_centres,
        "First Submission": earliest_dates,
        "Latest Submission": latest_dates,
        "Patients": patient_counts,
        "Image Studies": study_counts,
    }
    df = pd.DataFrame(data=d)
    df_sorted = df.sort_values(
        by=[order_column], ascending=(order_column == "Submitting Centre/Site")
    )

    table = dbc.Table.from_dataframe(df_sorted)
    return table


def create_hospital_counts(data, centre):
    patient = data.dataset("patient")
    if centre is None:
        title_filter = "All Submitting Centres"
    else:
        patient = patient[patient["SubmittingCentre"] == centre]
        title_filter = centre

    counts = (
        patient.rename(columns={"filename_covid_status": "Covid Status"})
        .groupby(["filename_earliest_date", "Covid Status"])
        .count()
        .sort_index()["Pseudonym"]
        .unstack()
        .cumsum()
        .fillna(method="ffill")
        .rename(columns={True: "Positive", False: "Negative"})
        .sort_index()
    )
    counts.index = pd.to_datetime(counts.index)

    # Extend time series on front and back
    extra = pd.DataFrame(
        [
            [0] * len(counts.columns),
            [counts[col].max() for col in counts.columns],
        ],
        columns=counts.columns,
        index=["2020-02-01", pd.to_datetime("today")],
    )
    extra.index = pd.to_datetime(extra.index)
    counts = counts.append(extra).sort_index()

    lines = []
    colors = {"Positive": "red", "Negative": "blue"}
    for group in colors:
        if group in counts:
            lines += [
                go.Scatter(
                    x=counts.index,
                    y=counts[group],
                    mode="lines",
                    name=group,
                    showlegend=True,
                    marker=dict(color=colors[group]),
                    line_shape="hv",
                )
            ]

    fig = go.Figure(
        data=lines,
        layout={
            "title": f"Cumulative Number of Patients by COVID status: {utils.escape(title_filter)}",
            "xaxis_title": "Date of upload to the warehouse before processing.",
        },
    )
    graph = dcc.Graph(id="example-graph", figure=fig)
    return graph
