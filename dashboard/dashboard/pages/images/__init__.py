from datetime import date

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
from pages import tools

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

    dataset_select = dcc.Dropdown(
        options=[
            {"label": "All all data", "value": "all"},
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
        Output("image-timeseries-plot", "children"),
        Input("dataset-select", "value"),
        Input("covid-status-select", "value"),
        Input("hospital-filter", "value"),
    )
    def set_image_series(group, covid_status, centre):
        return create_image_series(data, group, covid_status, centre)

    return app


def create_image_series(data, group, covid_status, centre):
    if centre is None:
        patient = data.data["patient"].copy()
    else:
        patient = data.data["patient"][
            data.data["patient"]["SubmittingCentre"] == centre
        ]

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
            [0, result.max()], index=["2020-05-25", pd.to_datetime("today")]
        )
        extra.index = pd.to_datetime(extra.index)
        result = result.append(extra).sort_index()
        return result

    target_patient_group = set(patient["Pseudonym"])

    ct_timeseries = get_image_timeseries(target_patient_group, data.data["ct"])
    xray_timeseries = get_image_timeseries(
        target_patient_group, data.data["xray"]
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
        layout={"title": f"Cumulative Number of Image Studies"},
    )
    graph = dcc.Graph(id="example-graph", figure=fig)
    return graph
