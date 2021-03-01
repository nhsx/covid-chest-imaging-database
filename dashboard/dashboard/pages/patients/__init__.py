import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from dataset import Dataset
from pages import tools
from pages.tools import numformat, show_last_update


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

    button_age_all_data = dbc.Button(
        "All Data",
        id="button_age_all_data",
        color="primary",
        outline=True,
    )
    button_age_train_val = dbc.Button(
        "Training / Validation",
        id="button_age_train_val",
        color="primary",
        outline=True,
    )
    button_age_pos_neg = dbc.Button(
        "Positive / Negative",
        id="button_age_pos_neg",
        color="primary",
        outline=True,
    )

    age_buttons = dbc.ButtonGroup(
        [
            button_age_all_data,
            button_age_train_val,
            button_age_pos_neg,
        ]
    )

    button_ethnicity_all_data = dbc.Button(
        "All Data",
        id="button_ethnicity_all_data",
        color="primary",
        outline=True,
    )
    button_ethnicity_train_val = dbc.Button(
        "Training / Validation",
        id="button_ethnicity_train_val",
        color="primary",
        outline=True,
    )
    button_ethnicity_pos_neg = dbc.Button(
        "Positive / Negative",
        id="button_ethnicity_pos_neg",
        color="primary",
        outline=True,
    )

    ethnicity_buttons = dbc.ButtonGroup(
        [
            button_ethnicity_all_data,
            button_ethnicity_train_val,
            button_ethnicity_pos_neg,
        ]
    )

    button_timeseries_all_data = dbc.Button(
        "All Data",
        id="button_timeseries_all_data",
        color="primary",
        outline=True,
    )

    button_timeseries_train_val = dbc.Button(
        "Training / Validation",
        id="button_timeseries_train_val",
        color="primary",
        outline=True,
    )
    button_timeseries_pos_neg = dbc.Button(
        "Positive / Negative",
        id="button_timeseries_pos_neg",
        color="primary",
        outline=True,
    )
    
    timeseries_buttons = dbc.ButtonGroup(
        [
            button_timeseries_all_data,
            button_timeseries_train_val,
            button_timeseries_pos_neg,   
        ]
    )

    age_selector = html.Div(
        [
            html.Div(
                children="""
                    Select chart to view:
                """
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [age_buttons],
                        ),
                        md=6,
                        sm=12,
                    ),
                ]
            ),
        ]
    )

    ethnicity_selector = html.Div(
        [
            html.Div(
                children="""
                    Select chart to view:
                """
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div([ethnicity_buttons]),
                        md=6,
                        sm=12,
                    ),
                ]
            ),
        ]
    )

    timeseries_selector = html.Div(
        [
            html.Div(
                children="""
                    Select chart to view:
                """
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div([timeseries_buttons]),
                        md=6,
                        sm=12,
                    ),
                ]
            ),
        ]
    )

    page = html.Div(
        children=[
            html.H1(children="Patients"),
            html.H2("Patients demographics breakdown"),
            html.H3("Gender"),
            create_gender_breakdown(data),
            html.Hr(),
            html.H3("Age"),
            age_selector,
            dcc.Loading(
                id="loading-age-data",
                type="dot",
                color="black",
                children=html.Div(id="age-breakdown-plot"),
            ),
            html.H3("Ethnicity"),
            ethnicity_selector,
            dcc.Loading(
                id="loading-ethnicity-data",
                type="dot",
                color="black",
                children=html.Div(id="ethnicity-breakdown-plot"),
            ),
            html.H3("RT-PCR swab dates"),
            timeseries_selector,
            dcc.Loading(
                id="loading-timeseries-data",
                type="dot",
                color="black",
                children=html.Div(id="timeseries-plot"),
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
        Output("age-breakdown-plot", "children"),
        Output("button_age_all_data", "outline"),
        Output("button_age_train_val", "outline"),
        Output("button_age_pos_neg", "outline"),
        Input("button_age_all_data", "n_clicks"),
        Input("button_age_train_val", "n_clicks"),
        Input("button_age_pos_neg", "n_clicks"),
    )
    def set_age_breakdown_buttons(
        n_clicks_all_data, n_clicks_train_val, n_clicks_pos_neg
    ):
        changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
        all_data_outline = train_val_outline = pos_neg_outline = True
        if changed_id == "button_age_all_data.n_clicks":
            group = "all"
            all_data_outline = False
        elif changed_id == "button_age_train_val.n_clicks":
            group = "train_val"
            train_val_outline = False
        elif changed_id == "button_age_pos_neg.n_clicks":
            group = "pos_neg"
            pos_neg_outline = False
        else:
            group = "all"
            all_data_outline = False

        return (
            create_age_breakdown(data, group),
            all_data_outline,
            train_val_outline,
            pos_neg_outline,
        )

    @app.callback(
        Output("ethnicity-breakdown-plot", "children"),
        Output("button_ethnicity_all_data", "outline"),
        Output("button_ethnicity_train_val", "outline"),
        Output("button_ethnicity_pos_neg", "outline"),
        Input("button_ethnicity_all_data", "n_clicks"),
        Input("button_ethnicity_train_val", "n_clicks"),
        Input("button_ethnicity_pos_neg", "n_clicks"),
    )
    def set_age_breakdown_buttons(
        n_clicks_all_data, n_clicks_train_val, n_clicks_pos_neg
    ):
        changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
        all_data_outline = train_val_outline = pos_neg_outline = True
        if changed_id == "button_ethnicity_all_data.n_clicks":
            group = "all"
            all_data_outline = False
        elif changed_id == "button_ethnicity_train_val.n_clicks":
            group = "train_val"
            train_val_outline = False
        elif changed_id == "button_ethnicity_pos_neg.n_clicks":
            group = "pos_neg"
            pos_neg_outline = False
        else:
            group = "all"
            all_data_outline = False

        return (
            create_ethnicity_breakdown(data, group),
            all_data_outline,
            train_val_outline,
            pos_neg_outline,
        )

    @app.callback(
        Output("timeseries-plot", "children"),
        Output("button_timeseries_all_data", "outline"),
        Output("button_timeseries_train_val", "outline"),
        Output("button_timeseries_pos_neg", "outline"),
        Input("button_timeseries_all_data", "n_clicks"),
        Input("button_timeseries_train_val", "n_clicks"),
        Input("button_timeseries_pos_neg", "n_clicks"),
    )
    def set_timeseries_buttons(
        n_clicks_all_data, n_clicks_train_val, n_clicks_pos_neg
    ):
        changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
        all_data_outline = train_val_outline = pos_neg_outline = True
        if changed_id == "button_timeseries_all_data.n_clicks":
            group = "all"
            all_data_outline = False
        elif changed_id == "button_timeseries_train_val.n_clicks":
            group = "train_val"
            train_val_outline = False
        elif changed_id == "button_timeseries_pos_neg.n_clicks":
            group = "pos_neg"
            pos_neg_outline = False
        else:
            group = "all"
            all_data_outline = False
        
        return (
            create_patient_timeseries(data, group),
            all_data_outline,
            train_val_outline,
            pos_neg_outline,
        )

    return app

def create_patient_timeseries(data, group):
    def aggregate_timeseries(df):
        timeseries = (
            df.groupby("all_swab_dates").count()["Pseudonym"]
            .groupby(pd.Grouper(freq="W"))
            .sum()
            .fillna(0)
            .sort_index()
        )
        return timeseries

    patient = data.data["patient"]
    patient["all_swab_dates"] = pd.to_datetime(
        patient["swab_date"].fillna(
            patient["date_of_positive_covid_swab"]
            )
        )
    if group == "all":
        timeseries = aggregate_timeseries(patient)

        lines = [
            go.Scatter(
                x=timeseries.index,
                y=timeseries,
                mode="lines",
                name="NCCID",
                showlegend=False,
                # marker=dict(color=colors[group]),
                line_shape="hv",
            ),
        ]
        
        fig = go.Figure(
            data=lines,
            layout={
                "title": "Number of patients by swab date across whole dataset",
                "xaxis_title": "Date",
                "yaxis_title": "# of Patients",
            }
        )
    elif group == "train_val":
        training_series = aggregate_timeseries(patient[patient["group"] == "training"])
        validation_series = aggregate_timeseries(patient[patient["group"] == "validation"])
        lines = [
            go.Scatter(
                x=training_series.index,
                y=training_series,
                mode="lines",
                name="Training",
                showlegend=True,
                line_shape="hv",
            ),
            go.Scatter(
                x=validation_series.index,
                y=validation_series,
                mode="lines",
                name="Validation",
                showlegend=True,
                line_shape="hv",
            ),
        ]
        fig = go.Figure(
            data=lines,
            layout={
                "title": "Number of patients by swab date across training/validation sets",
                "xaxis_title": "Date",
                "yaxis_title": "# of Patients",
            }
        )
    elif group == "pos_neg":
        positive_series = aggregate_timeseries(patient[patient["filename_covid_status"]])
        negative_series = aggregate_timeseries(patient[~patient["filename_covid_status"]])
        lines = [
            go.Scatter(
                x=negative_series.index,
                y=negative_series,
                mode="lines",
                name="Negative",
                showlegend=True,
                line_shape="hv",
            ),
            go.Scatter(
                x=positive_series.index,
                y=positive_series,
                mode="lines",
                name="Positive",
                showlegend=True,
                line_shape="hv",
            ),
        ]

        fig = go.Figure(
            data = lines,
            layout={
                "title": "Number of patients by swab date across positive/negative patients",
                "xaxis_title": "Date",
                "yaxis_title": "# of Patients",
            }
        )

    graph = dcc.Graph(id="timeseries", figure=fig)
    return graph



def create_age_breakdown(data, group):
    def biground(x, base=5):
        return base * round(x / base)

    patient = data.data["patient"]

    xbins = dict(  # bins used for histogram
        start=0, end=biground(patient["age_update"].max()), size=5
    )

    if group == "all":

        fig = go.Figure(
            layout={
                "title": "Age distribution across whole dataset",
                "xaxis_title": "Age",
                "yaxis_title": "% of Patients",
            },
        )
        fig.add_trace(
            go.Histogram(
                x=patient["age_update"],
                histnorm="percent",
                xbins=xbins,
            )
        )

    elif group == "train_val":
        patient_training = patient[patient["group"] == "training"]
        patient_validation = patient[patient["group"] == "validation"]
        fig = go.Figure(
            layout={
                "title": "Age distribution in training and validation sets",
                "xaxis_title": "Age",
                "yaxis_title": "% of Patients",
                "legend_title": "Group",
            },
        )
        fig.add_trace(
            go.Histogram(
                x=patient_training["age_update"],
                name="Training",
                histnorm="percent",
                xbins=xbins,
            )
        )
        fig.add_trace(
            go.Histogram(
                x=patient_validation["age_update"],
                name="Validation",
                histnorm="percent",
                xbins=xbins,
            )
        )
    elif group == "pos_neg":
        patient_postive = patient[patient["filename_covid_status"]]
        patient_negative = patient[~patient["filename_covid_status"]]
        fig = go.Figure(
            layout={
                "title": "Age distribution in covid positive and negative patients",
                "xaxis_title": "Age",
                "yaxis_title": "% of Patients",
                "legend_title": "Group",
            },
        )
        fig.add_trace(
            go.Histogram(
                x=patient_negative["age_update"],
                name="Negative",
                histnorm="percent",
                xbins=xbins,
            )
        )
        fig.add_trace(
            go.Histogram(
                x=patient_postive["age_update"],
                name="Positive",
                histnorm="percent",
                xbins=xbins,
            )
        )
        

    fig.update_layout(barmode="overlay")
    fig.update_traces(opacity=0.75)

    graph = dcc.Graph(id="age-histogram", figure=fig)
    return graph


def create_ethnicity_breakdown(data, group):
    patient = data.data["patient"]

    # The following ensures that histogram categories are plotted in total frequency order
    ethnic_groups = list(
        patient["ethnicity"].value_counts(ascending=True).keys()
    )
    ethnic_group_index = dict(zip(ethnic_groups, range(len(ethnic_groups))))
    patient["ethnicity_frequency_rank"] = patient["ethnicity"].map(
        ethnic_group_index
    )
    patient = patient.sort_values(["ethnicity_frequency_rank"], ascending=True)

    if group == "all":
        fig = go.Figure(
            layout={
                "title": "Ethnicity distribution across whole dataset",
                "xaxis_title": "Ethnicity",
                "yaxis_title": "% of Patients",
            },
        )
        fig.add_trace(
            go.Histogram(
                x=patient["ethnicity"],
                histnorm="percent",
            )
        )
    elif group == "train_val":
        patient_training = patient[patient["group"] == "training"]
        patient_validation = patient[patient["group"] == "validation"]
        fig = go.Figure(
            layout={
                "title": "Ethnicity distribution in training and validation sets",
                "xaxis_title": "Ethnicity",
                "yaxis_title": "% of Patients",
                "legend_title": "Group",
            },
        )
        fig.add_trace(
            go.Histogram(
                x=patient_training["ethnicity"],
                name="Training",
                histnorm="percent",
            )
        )
        fig.add_trace(
            go.Histogram(
                x=patient_validation["ethnicity"],
                name="Validation",
                histnorm="percent",
            )
        )
    elif group == "pos_neg":
        patient_postive = patient[patient["filename_covid_status"]]
        patient_negative = patient[~patient["filename_covid_status"]]
        fig = go.Figure(
            layout={
                "title": "Ethnicity distribution in covid positive and negative patients",
                "xaxis_title": "Ethnicity",
                "yaxis_title": "% of Patients",
                "legend_title": "Covid status",
            },
        )
        fig.add_trace(
            go.Histogram(
                x=patient_negative["ethnicity"],
                name="Negative",
                histnorm="percent",
            )
        )
        fig.add_trace(
            go.Histogram(
                x=patient_postive["ethnicity"],
                name="Positive",
                histnorm="percent",
            )
        )
        

    graph = dcc.Graph(id="ethnicity-histogram", figure=fig)
    return graph


def create_gender_breakdown(data):
    patient = data.data["patient"]
    total = patient["sex_update"].value_counts()
    training = patient[patient["group"] == "training"][
        "sex_update"
    ].value_counts()
    validation = patient[patient["group"] == "validation"][
        "sex_update"
    ].value_counts()
    n_patients = patient.count()

    # total_column = [f"{numformat(total['M'])} ({total['M']/n_patients:.1f}%)",
    #  f"{total['F']}", f"{total['Unknown']}", 0]

    def calculate_column(dataset):
        genders = ["M", "F", "Unknown"]
        num = sum([dataset[g] for g in genders])
        column = [
            "{} ({:.1%})".format(numformat(dataset[g]), dataset[g] / num)
            for g in genders
        ]
        n_mf = dataset["M"] + dataset["F"]
        column += [
            "{:d}:{:d}%".format(
                round(dataset["M"] / n_mf * 100),
                round(dataset["F"] / n_mf * 100),
            )
        ]
        return column

    gender = {
        "Gender": ["Male", "Female", "Unknown", "Male:Female ratio"],
        "Total": calculate_column(total),
        "Training set": calculate_column(training),
        "Validation set": calculate_column(validation),
    }

    df = pd.DataFrame(
        gender, columns=["Gender", "Total", "Training set", "Validation set"]
    )

    table = dbc.Table.from_dataframe(df)
    return table
