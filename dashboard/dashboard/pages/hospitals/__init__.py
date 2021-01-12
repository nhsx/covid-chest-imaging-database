import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from flask_caching import Cache
from pages import tools
from dataset import Dataset

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
    table_header = [
        html.Thead(
            html.Tr([html.Th("Metric"), html.Th("Value")]),
            className="thead-dark",
        )
    ]

    patient = data.data["patient"]
    number_trusts = patient["SubmittingCentre"].nunique()
    number_patients = patient["Pseudonym"].nunique()

    ct = data.data["ct"]
    number_ct_studies = ct["StudyInstanceUID"].nunique()
    mri = data.data["mri"]
    number_mri_studies = mri["StudyInstanceUID"].nunique()
    xray = data.data["xray"]
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
        [html.Td("Number of Xray studies"), html.Td(number_xray_studies)],
        className="table-danger"
    )

    table_body = [html.Tbody([row1, row2, row3, row4, row5])]

    table = dbc.Table(
        table_header + table_body,
        bordered=True,
        responsive=True,
    )


    card_content = [
        dbc.CardHeader("Work in Progress"),
        dbc.CardBody(
            [
                html.P(
                    "This page is not yet filled in.",
                    className="card-text",
                ),
            ]
        ),
    ]

    page = html.Div(
        children=[
            html.H1(children="Hospital Sites"),
            dbc.Alert("👷 This page hasn't been filled in yet.", color="warning")
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