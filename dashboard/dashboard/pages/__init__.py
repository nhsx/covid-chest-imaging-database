
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

import dash
import dash_bootstrap_components as dbc

from .summary import create_app as summary_create_app

SERVE_LOCALLY = os.getenv("DBC_DOCS_MODE", "production") == "dev"

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

#use importlib to import all the pages!
# https://stackoverflow.com/a/31661374/171237

def register_pages(dataset):
    pages = {"summary" : {"creator": summary_create_app}, "test": {}, "other": {}}

    sidenav_items = [
        {
            "name": "quickstart",
            "href": "/docs/quickstart",
            "label": "Quickstart",
        }
    ]
    sidenav_items += [
            {
                "name": slug,
                "href": f"/pages/{slug}",
                "label": slug,
            } for slug in pages
    ]
    print(sidenav_items)

    routes = {}
    env = Environment(loader=FileSystemLoader(TEMPLATES.as_posix()))
    template = env.from_string(INDEX_STRING_TEMPLATE)

    # for slug in pages:
    #     app = dash.Dash(
    #         external_stylesheets=["/static/loading.css"],
    #         requests_pathname_prefix=f"/docs/components/{slug}/",
    #         suppress_callback_exceptions=True,
    #         serve_locally=SERVE_LOCALLY,
    #         index_string=template.render(
    #             sidenav_items=sidenav_items,
    #             sidenav_active="components",
    #             active_child=slug,
    #         ),
    #         update_title=None,
    #     )
    #     app.title = f"{_get_label(slug)} - dbc docs"

    #     routes[f"/docs/components/{slug}"] = app


    # kwargs = {
    #     "external_stylesheets": ["/static/loading.css", dbc.themes.SKETCHY],
    #     "requests_pathname_prefix": "/pages/page1/",
    #     "serve_locally": SERVE_LOCALLY,
    #     "suppress_callback_exceptions": True,
    #     "index_string":template.render(
    #             sidenav_items=sidenav_items,
    #             sidenav_active="components",
    #             active_child="page1",
    #         ),
    #     "update_title": None,
    # }
    # app = page1.create_app(data, dataset, **kwargs)
    # app.title = f"NCCID > Page1 "
    # routes[f"/pages/page1"] = app

    kwargs = {
        "external_stylesheets": ["/static/loading.css", dbc.themes.SKETCHY],
        "requests_pathname_prefix": "/pages/summary/",
        "serve_locally": SERVE_LOCALLY,
        "suppress_callback_exceptions": True,
        "index_string":template.render(
                sidenav_items=sidenav_items,
                sidenav_active="summary",
                # active_child="summary",
            ),
        "update_title": None,
    }
    app = summary_create_app(dataset, **kwargs)
    app.title = f"NCCID > Summary "
    routes[f"/pages/summary"] = app
    return routes