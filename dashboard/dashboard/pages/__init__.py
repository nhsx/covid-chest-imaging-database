"""Create and manage all the pages in the dashboard

"""

import os
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from flask import render_template_string
from jinja2 import Environment, FileSystemLoader

from dataset import Dataset

from .hospitals import create_app as hospitals_create_app
from .images import create_app as images_create_app
from .patients import create_app as patients_create_app
from .quality import create_app as data_quality_create_app
from .summary import create_app as summary_create_app

SERVE_LOCALLY = True
HERE = Path(__file__).parent
TEMPLATES = HERE.parent / "templates"

INDEX_STRING_TEMPLATE = """{% from "macros/navbar.html" import navbar %}
{% extends "pages.html" %}
{% block head %}
{{ super() }}
{{ "{%metas%}{%css%}" }}
{% endblock %}
{% block title %}
<title>{{ "{%title%}" }}</title>
{% endblock %}
{% block header %}{{ navbar("pages") }}{% endblock %}
{% block content %}
{{ "{%app_entry%}" }}
{% endblock %}
{% block scripts %}
<footer>
  {{ "{%config%}{%scripts%}{%renderer%}" }}
  {{ super() }}
</footer>
{% endblock %}
"""


def _url_format(slug):
    return slug.replace(" ", "_")


def register_pages(data: Dataset, server):
    """Create all the Dash app pages and register themwith a Flask
    server.

    Parameters
    ----------
    data : dataset.Dataset
        The main dataset which is used for analysis.
    server :
        The server which is hosting all these pages.

    Returns
    -------
    dict
        A mapping for routes -> Dash app for the server implement
    """
    pages = {
        "summary": {"creator": summary_create_app},
        "hospital sites": {"creator": hospitals_create_app},
        "patients": {"creator": patients_create_app},
        "images": {"creator": images_create_app},
        "data quality": {"creator": data_quality_create_app},
    }

    sidenav_items = [
        {
            "name": _url_format(slug),
            "href": f"/pages/{_url_format(slug)}",
            "label": slug.title(),
        }
        for slug in pages
    ]

    routes = {}
    env = Environment(loader=FileSystemLoader(TEMPLATES.as_posix()))
    template = env.from_string(INDEX_STRING_TEMPLATE)

    for slug in pages:
        kwargs = {
            "external_stylesheets": [
                "/static/loading.css",
                dbc.themes.SKETCHY,
            ],
            "serve_locally": SERVE_LOCALLY,
            "suppress_callback_exceptions": True,
            "index_string": template.render(
                sidenav_items=sidenav_items,
                sidenav_active=_url_format(slug),
            ),
            "update_title": None,
            "server": server,
            "routes_pathname_prefix": f"/pages/{_url_format(slug)}/",
        }
        app = pages[slug]["creator"](data, **kwargs)
        app.title = f"NCCID > {slug.title()}"
        routes[f"/pages/{_url_format(slug)}"] = app

    return routes
