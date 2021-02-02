import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from dataset import Dataset
from pages.tools import numformat


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
            html.H2("Sites Overview"),
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
            dcc.Loading(
                id="loading-hospital-table",
                type="dot",
                color="black",
                children=html.Div(id="hospital-table"),
            ),
            # html.Div(id="hospital-table"),
            # html.Br(),
            # html.Div(id="hospital-datatable"),
            html.Hr(),
            html.H2("Data Over Time"),
            # html.Br(),
            dcc.Loading(
                id="loading-patients-swabs",
                type="dot",
                color="black",
                children=html.Div(id="patients-swabs"),
            ),
            html.Label(
                [
                    "Select Submitting Centre/Site to filter above",
                ],
                htmlFor="hospital-filter",
            ),
            centres_select,
            html.P(
                "Note: click the × mark to clear the selection above and show data for all submitting centres.",
                id="centres-note",
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

    app.layout = lambda: serve_layout(data)

    @app.callback(
        Output("hospital-table", "children"),
        Input("covid-status", "value"),
        Input("table-order", "value"),
    )
    def set_hostpital_table(covid_status, order_column):
        return create_hospital_table(data, covid_status, order_column)

    # @app.callback(
    #     Output("hospital-datatable", "children"),
    #     [Input("covid-status", "value")],
    # )
    # def set_hostpital_datatable(value):
    #     return create_hospital_datatable(data, value)

    @app.callback(
        Output("patients-swabs", "children"),
        [Input("hospital-filter", "value")],
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
    df_sorted = df.sort_values(
        by=[order_column], ascending=(order_column == "Submitting Centre/Site")
    )

    # rows = []
    # for index, row in df_sorted.iterrows():
    #     rows += [
    #         html.Tr(
    #             [
    #                 html.Td(row["Submitting Centre/Site"]),
    #                 html.Td(row["First Submission"]),
    #                 html.Td(
    #                     numformat(row["Patients"]), className="text-right"
    #                 ),
    #                 html.Td(
    #                     numformat(row["Image Studies"]), className="text-right"
    #                 ),
    #             ]
    #         )
    #     ]
    # table_body = [html.Tbody(rows)]
    # table = dbc.Table(table_header + table_body, bordered=True)

    table = dbc.Table.from_dataframe(df_sorted)
    return table


# def create_hospital_datatable(data, covid_status):
#     patient = data.data["patient"]
#     if covid_status == "positive":
#         patient = patient[patient["filename_covid_status"]]
#     elif covid_status == "negative":
#         patient = patient[~patient["filename_covid_status"]]

#     ct = data.data["ct"]
#     mri = data.data["mri"]
#     xray = data.data["xray"]

#     submitting_centres = sorted(patient["SubmittingCentre"].unique())
#     earliest_dates = []
#     patient_counts = []
#     study_counts = []
#     for centre in submitting_centres:
#         patient_ids = set(
#             patient[patient["SubmittingCentre"] == centre]["Pseudonym"]
#         )
#         patient_counts += [len(patient_ids)]
#         ct_studies = ct[ct["Pseudonym"].isin(patient_ids)][
#             "StudyInstanceUID"
#         ].nunique()
#         mri_studies = mri[mri["Pseudonym"].isin(patient_ids)][
#             "StudyInstanceUID"
#         ].nunique()
#         xray_studies = xray[xray["Pseudonym"].isin(patient_ids)][
#             "StudyInstanceUID"
#         ].nunique()
#         study_counts += [ct_studies + mri_studies + xray_studies]

#         earliest = patient[patient["SubmittingCentre"] == centre][
#             "filename_earliest_date"
#         ].min()
#         earliest_dates += [earliest]

#     d = {
#         "Submitting Centres/Sites": submitting_centres,
#         "First Submission": earliest_dates,
#         "Patients": patient_counts,
#         "Image Studies": study_counts,
#     }
#     df = pd.DataFrame(data=d)
#     table = dash_table.DataTable(
#         id="table",
#         columns=[{"name": i, "id": i} for i in df.columns],
#         data=df.to_dict("records"),
#         sort_action="native",
#     )

#     return table


def create_hospital_counts(data, centre):
    if centre is None:
        title_filter = "All Submitting Centres"
        patient = data.data["patient"].copy()
    else:
        patient = data.data["patient"][
            data.data["patient"]["SubmittingCentre"] == centre
        ]
        title_filter = centre

    # patients["latest_swab_date"] = pd.to_datetime(patients["latest_swab_date"])

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
        index=["2020-05-10", pd.to_datetime("today")],
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
            "title": f"Cumulative Number of Patients by COVID status: {title_filter}",
            "xaxis_title": "Date of upload to the warehouse before processing.",
        },
    )
    graph = dcc.Graph(id="example-graph", figure=fig)
    return graph
