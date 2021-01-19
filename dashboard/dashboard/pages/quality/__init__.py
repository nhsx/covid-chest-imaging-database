import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
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

    page = html.Div(
        children=[
            html.H1(children="Data Quality"),
            dbc.Alert(
                "👷 This page hasn't been filled in yet.", color="warning"
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

    return app
