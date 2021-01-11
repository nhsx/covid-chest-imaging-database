import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from flask_caching import Cache

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
cache = Cache(config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=10)
def serve_layout(dataset):
    # assume you have a "long-form" data frame
    # see https://plotly.com/python/px-arguments/ for more options
    df = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    })

    fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

    text_input = html.Div(
    [
        dbc.Input(id="input", placeholder="Type something...", type="text"),
        html.Br(),
        html.P(id="output"),
    ]
    )

    buttons = html.Div(
        [
            dbc.Button("Primary", color="primary", className="mr-1"),
            dbc.Button("Secondary", color="secondary", className="mr-1"),
            dbc.Button("Success", color="success", className="mr-1"),
            dbc.Button("Warning", color="warning", className="mr-1"),
            dbc.Button("Danger", color="danger", className="mr-1"),
            dbc.Button("Info", color="info", className="mr-1"),
            dbc.Button("Light", color="light", className="mr-1"),
            dbc.Button("Dark", color="dark", className="mr-1"),
            dbc.Button("Link", color="link"),
        ]
    )

    badge = dbc.Button(
    ["DataCounter", dbc.Badge(dataset.get_counter(), color="light", className="ml-1")],
    color="primary",
    )

    return html.Div(children=[
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        badge,

        dcc.Graph(
            id='example-graph',
            figure=fig
        ),

        text_input,

        buttons
    ])

def create_app(dataset, **kwargs):
    app = dash.Dash(__name__, **kwargs)
    cache.init_app(app.server)

    # # assume you have a "long-form" data frame
    # # see https://plotly.com/python/px-arguments/ for more options
    # df = pd.DataFrame({
    #     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    #     "Amount": [4, 1, 2, 2, 4, 5],
    #     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    # })

    # fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

    # text_input = html.Div(
    # [
    #     dbc.Input(id="input", placeholder="Type something...", type="text"),
    #     html.Br(),
    #     html.P(id="output"),
    # ]
    # )

    # buttons = html.Div(
    #     [
    #         dbc.Button("Primary", color="primary", className="mr-1"),
    #         dbc.Button("Secondary", color="secondary", className="mr-1"),
    #         dbc.Button("Success", color="success", className="mr-1"),
    #         dbc.Button("Warning", color="warning", className="mr-1"),
    #         dbc.Button("Danger", color="danger", className="mr-1"),
    #         dbc.Button("Info", color="info", className="mr-1"),
    #         dbc.Button("Light", color="light", className="mr-1"),
    #         dbc.Button("Dark", color="dark", className="mr-1"),
    #         dbc.Button("Link", color="link"),
    #     ]
    # )

    # badge = dbc.Button(
    # ["DataCounter", dbc.Badge(dataset.get_counter(), color="light", className="ml-1")],
    # color="primary",
    # )

    # app.layout = html.Div(children=[
    #     html.H1(children='Hello Dash'),

    #     html.Div(children='''
    #         Dash: A web application framework for Python.
    #     '''),

    #     badge,

    #     dcc.Graph(
    #         id='example-graph',
    #         figure=fig
    #     ), 

    #     text_input,

    #     buttons
    # ])
    app.layout = lambda : serve_layout(dataset)

    @app.callback(Output("output", "children"), [Input("input", "value")])
    def output_text(value):
        return capital(value)
    return app


def capital(text):
    return text.title() if text else ''