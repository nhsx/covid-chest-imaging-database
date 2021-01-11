import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "simple"})


@cache.cached(timeout=60)
def serve_layout(dataset):

    table_header = [
        html.Thead(
            html.Tr([html.Th("Metric"), html.Th("Value")]),
            className="thead-dark",
        )
    ]

    patient = dataset.data["patient"]
    number_trusts = patient["SubmittingCentre"].nunique()
    number_patients = patient["Pseudonym"].nunique()

    ct = dataset.data["ct"]
    number_ct_studies = ct["StudyInstanceUID"].nunique()
    mri = dataset.data["mri"]
    number_mri_studies = mri["StudyInstanceUID"].nunique()
    xray = dataset.data["xray"]
    number_xray_studies = xray["StudyInstanceUID"].nunique()

    row1 = html.Tr([html.Td("Total number of trusts"), html.Td(number_trusts)])
    row2 = html.Tr(
        [html.Td("Total number of patients"), html.Td(number_patients)]
    )
    row3 = html.Tr(
        [html.Td("Number of CT studies"), html.Td(number_ct_studies)]
    )
    row4 = html.Tr(
        [html.Td("Number of MRI studies"), html.Td(number_mri_studies)]
    )
    row5 = html.Tr(
        [html.Td("Number of Xray studies"), html.Td(number_xray_studies)]
    )

    table_body = [html.Tbody([row1, row2, row3, row4, row5])]

    table = dbc.Table(
        table_header + table_body,
        bordered=True,
        responsive=True,
        hover=True,
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
        ]
    )
    return page


def create_app(dataset, **kwargs):
    app = dash.Dash(__name__, **kwargs)
    cache.init_app(app.server)

    app.layout = lambda: serve_layout(dataset)

    return app


def capital(text):
    return text.title() if text else ""
