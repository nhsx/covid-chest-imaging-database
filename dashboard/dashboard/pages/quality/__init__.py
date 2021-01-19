import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
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
    covid_positives = patient.loc[patient.filename_covid_status]
    completeness = pd.DataFrame(
        {
            "Not-Null": (
                (~covid_positives.isnull()).sum() * 100 / len(covid_positives)
            ),
            "Nulls": (
                covid_positives.isnull().sum() * 100 / len(covid_positives)
            ),
        }
    ).sort_values(by="Nulls")
    fig = px.bar(completeness, x=completeness.index, y=["Nulls", "Not-Null"])
    fig.update_layout(
        barmode="stack",
        xaxis_tickangle=-45,
        title="Completeness of Fields (Covid Positive only)",
        xaxis_title="Fields",
        yaxis_title="% of Nulls",
        legend_title="",
    )
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x")

    graph = dcc.Graph(id="completeness-graph", figure=fig)

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
            graph,
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
