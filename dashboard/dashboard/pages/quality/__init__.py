import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from . import columns
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
    patient = data.data["patient"]
    centres = sorted(patient["SubmittingCentre"].unique())
    centres_select = dcc.Dropdown(
        placeholder="Select a submitting site / centre to filter",
        options=[{"label": centre, "value": centre} for centre in centres],
        id="hospital-filter",
    )

    columns_values = [
        {"label": f"{key} fields", "value": key} for key in columns.COLS_MAP
    ]
    variables_select = dcc.Dropdown(
        options=[
            {"label": f"{key} fields", "value": key}
            for key in columns.COLS_MAP
        ],
        value="All",
        clearable=False,
        id="variables-filter",
    )

    sort_by_select = dcc.Dropdown(
        options=[
            {"label": "Completeness", "value": "Completeness"},
            {"label": "Field Name", "value": "Field"},
        ],
        value="Completeness",
        clearable=False,
        id="sortby-select",
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
                                        "Submitting centre filtering.",
                                    ],
                                    htmlFor="hospital-filter",
                                ),
                                centres_select,
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
                                        "Select fields to show.",
                                    ],
                                    htmlFor="variables-filter",
                                ),
                                variables_select,
                            ]
                        ),
                        md=3,
                        sm=12,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.Label(
                                    [
                                        "Sort by.",
                                    ],
                                    htmlFor="sortby-select",
                                ),
                                sort_by_select,
                            ]
                        ),
                        md=3,
                        sm=12,
                    ),
                ]
            )
        ]
    )

    page = html.Div(
        children=[
            html.H1(children="Data Quality"),
            html.H2("Completeness of Fields"),
            html.P(
                "Completeness of the clinical data after applying the "
                + "cleaning pipeline, which removes erroneous entries such "
                + "as blank spaces, extracts numerical measurements from "
                + "string entries, and fills missing demographics using "
                + "DICOM header information. For each field of the clinical "
                + "data, the percentage of entries with non-null values are "
                + "shown against the percentage of null values."
            ),
            selector,
            dcc.Loading(
                id="completeness-chart-loader",
                type="dot",
                color="black",
                children=html.Div(id="completeness-chart"),
            ),
            html.Hr(),
            dcc.Loading(
                id="completeness-table-loader",
                type="dot",
                color="black",
                children=html.Div(id="completeness-table"),
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
        Output("completeness-chart", "children"),
        Input("hospital-filter", "value"),
        Input("variables-filter", "value"),
        Input("sortby-select", "value"),
    )
    def set_completeness_chart(centre, fields, sort_by):
        return create_completeness_chart(data, centre, fields, sort_by)

    @app.callback(
        Output("completeness-table", "children"),
        Input("hospital-filter", "value"),
        Input("variables-filter", "value"),
        Input("sortby-select", "value"),
    )
    def set_completeness_table(centre, fields, sort_by):
        return create_completeness_table(data, centre, fields, sort_by)

    return app


def create_completeness_chart(data, centre, fields, sort_by):
    patient = data.data["patient"]
    covid_positives = patient.loc[patient.filename_covid_status]

    if centre is not None:
        covid_positives = covid_positives[
            covid_positives["SubmittingCentre"] == centre
        ]
    else:
        centre = "All centres"

    covid_positives = covid_positives[columns.COLS_MAP[fields]]
    if covid_positives.empty:
        return dbc.Alert(
            f"{centre} doesn't seem to have any positive patients, please select another centre!",
            color="warning",
        )

    completeness = pd.DataFrame(
        {
            "Not-Null": (
                (~covid_positives.isnull()).sum() * 100 / len(covid_positives)
            ),
            "Nulls": (
                covid_positives.isnull().sum() * 100 / len(covid_positives)
            ),
        }
    )
    if sort_by == "Completeness":
        completeness = completeness.sort_values(by="Nulls")
    elif sort_by == "Field":
        completeness = completeness.sort_index()
    completeness["Not-Null"].fillna(0)
    completeness["Nulls"].fillna(100)

    fig = px.bar(
        completeness,
        x=completeness.index,
        y=["Not-Null", "Nulls"],
        color_discrete_map={"Nulls": "#d62728", "Not-Null": "#1f77b4"},
    )

    fig.update_layout(
        barmode="stack",
        xaxis_tickangle=-45,
        title=f"Completeness of Fields (Covid Positive only): {centre}, {fields} fields",
        xaxis_title="Fields",
        yaxis_title="% of Nulls",
        legend_title="",
    )
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x")

    graph = dcc.Graph(id="completeness-graph", figure=fig)
    return graph


def create_completeness_table(data, centre, fields, sort_by):
    patient = data.data["patient"]
    covid_positives = patient.loc[patient.filename_covid_status]

    if centre is not None:
        covid_positives = covid_positives[
            covid_positives["SubmittingCentre"] == centre
        ]

    covid_positives = covid_positives[columns.COLS_MAP[fields]]
    if covid_positives.empty:
        # The graph already sends a warning, no need here
        return html.Span()

    completeness = (
        pd.DataFrame(
            {
                "Completeness": (
                    (~covid_positives.isnull()).sum()
                    * 100
                    / len(covid_positives)
                ),
            }
        )
        .sort_values(by="Completeness", ascending=False)
        .reset_index()
        .rename(columns={"index": "Field"})
    )
    completeness["Completeness"].fillna(0)

    if sort_by == "Completeness":
        completeness = completeness.sort_values(
            by="Completeness", ascending=False
        )
    elif sort_by == "Field":
        completeness = completeness.sort_values(by="Field")

    completeness["Completeness"] = completeness["Completeness"].apply(
        lambda x: f"{x:.0f}%"
    )

    table = dbc.Table.from_dataframe(
        completeness, striped=True, bordered=True, hover=True
    )
    return table
