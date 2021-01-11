import os
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from jinja2 import Environment, FileSystemLoader

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
{% block header %}{{ navbar("docs") }}{% endblock %}
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


def register_pages(dataset):
    pages = {"summary": {"creator": summary_create_app}}

    sidenav_items = [
        {
            "name": slug,
            "href": f"/pages/{slug}",
            "label": slug.capitalize(),
        }
        for slug in pages
    ]

    routes = {}
    env = Environment(loader=FileSystemLoader(TEMPLATES.as_posix()))
    template = env.from_string(INDEX_STRING_TEMPLATE)

    for slug in pages:
        kwargs = {
            "external_stylesheets": ["/static/loading.css", dbc.themes.SKETCHY],
            "requests_pathname_prefix": "/pages/summary/",
            "serve_locally": SERVE_LOCALLY,
            "suppress_callback_exceptions": True,
            "index_string": template.render(
                sidenav_items=sidenav_items,
                sidenav_active=slug,
                # active_child="summary",
            ),
            "update_title": None,
        }
        app = pages[slug]["creator"](dataset, **kwargs)
        app.title = f"NCCID > {slug.capitalize}"
        routes[f"/pages/{slug}"] = app

    return routes
