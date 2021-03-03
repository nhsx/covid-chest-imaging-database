import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

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

    dataset_select = dcc.Dropdown(
        options=[
            {"label": "All data", "value": "all"},
            {"label": "Training set", "value": "training"},
            {"label": "Validation set", "value": "validation"},
        ],
        value="all",
        clearable=False,
        id="dataset-select",
    )

    covid_status_select = dcc.Dropdown(
        options=[
            {"label": "All patients", "value": "all"},
            {"label": "Positive patients", "value": "positive"},
            {"label": "Negative patients", "value": "negative"},
        ],
        value="all",
        clearable=False,
        id="covid-status-select",
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
                                        "Select dataset",
                                    ],
                                    htmlFor="dataset-select",
                                ),
                                dataset_select,
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
                                        "Select COVID-19 status",
                                    ],
                                    htmlFor="covid-status-select",
                                ),
                                covid_status_select,
                            ]
                        ),
                        md=6,
                        sm=12,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Label(
                                    [
                                        "Select Submitting Centre/Site to filter",
                                    ],
                                    htmlFor="hospital-filter",
                                ),
                                centres_select,
                            ]
                        ),
                        md=12,
                    )
                ]
            ),
        ]
    )

    page = html.Div(
        children=[
            html.H1(children="Images"),
            selector,
            dcc.Loading(
                id="loading-image-timeseries-plot",
                type="dot",
                color="black",
                children=html.Div(id="image-timeseries-plot"),
            ),
            dbc.Alert(
                "ⓘ Data collection for the NCCID began in May 2020 "
                + " but includes images taken in hospital since Februray 2020.",
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
        Output("image-timeseries-plot", "children"),
        [
            Input("dataset-select", "value"),
            Input("covid-status-select", "value"),
            Input("hospital-filter", "value"),
        ],
    )
    def set_image_series(group, covid_status, centre):
        return create_image_series(data, group, covid_status, centre)

    return app


def create_image_series(data, group, covid_status, centre):
    patient = data.dataset("patient")
    if centre is not None:
        patient = patient[patient["SubmittingCentre"] == centre]

    if covid_status == "positive":
        patient = patient[patient["filename_covid_status"]]
    elif covid_status == "negative":
        patient = patient[~patient["filename_covid_status"]]

    if group != "all":
        patient = patient[patient["group"] == group]

    def get_image_timeseries(patients, modality):
        df = modality[modality["Pseudonym"].isin(patients)].copy()
        df["last_modified"] = pd.to_datetime(df["last_modified"])
        result = (
            df.drop_duplicates("StudyInstanceUID", keep="first")
            .groupby(["last_modified"])
            .count()
            .sort_index()["StudyInstanceUID"]
            .cumsum()
        )
        # Extend time series on front and back
        extra = pd.Series(
            [0, result.max()], index=["2020-02-01", pd.to_datetime("today")]
        )
        extra.index = pd.to_datetime(extra.index)
        result = result.append(extra).sort_index()
        return result

    target_patient_group = set(patient["Pseudonym"])

    ct_timeseries = get_image_timeseries(
        target_patient_group, data.dataset("ct")
    )
    xray_timeseries = get_image_timeseries(
        target_patient_group, data.dataset("xray")
    )

    lines = [
        go.Scatter(
            x=ct_timeseries.index,
            y=ct_timeseries,
            mode="lines",
            name="CT Studies",
            showlegend=True,
            # marker=dict(color=colors[group]),
            line_shape="hv",
        ),
        go.Scatter(
            x=xray_timeseries.index,
            y=xray_timeseries,
            mode="lines",
            name="X-ray Studies",
            showlegend=True,
            # marker=dict(color=colors[group]),
            line_shape="hv",
        ),
    ]

    fig = go.Figure(
        data=lines,
        layout={
            "title": "Cumulative Number of Image Studies",
            "xaxis_title": "Date of release to data users",
        },
    )
    graph = dcc.Graph(id="example-graph", figure=fig)
    return graph
