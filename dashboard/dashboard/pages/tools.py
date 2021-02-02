""" Common helper functions for the dashboard pages.

Certain tasks might happen frequently in the dashboard pages
and thus having a central implementation helps eliminating code
duplications where it is possible.
"""

import time

import dash_html_components as html


def numformat(number: int) -> str:
    """Format a number according to our convention

    Parameters
    ----------
    number : int
        A number to format

    Returns
    -------
    str
        The formatted number
    """
    return f"{number:,.0f}"


def show_last_update(data):
    """Element to display in a page, showing the last update
    by the underlying data storage."""
    t = time.strftime("%c", data.get_last_update())
    return html.Div(f"Data last updated: {t}")
