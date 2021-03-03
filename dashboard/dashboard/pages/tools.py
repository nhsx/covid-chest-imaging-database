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


def storage_format(number: int) -> str:
    """Format a number representing a bytes of storage according to our convention
    Uses convention that 1 GB = 1000^3 bytes

    Parameters
    ----------
    number : int
        A number of bytes to format

    Returns
    -------
    str
        The formatted storage string
    """
    GBs = float(number) / float(1000 ** 3)
    if GBs > 100:
        GBs = round(GBs)
        GBs_str = f"{GBs} GB"
    else:
        GBs_str = f"{GBs:,.1f} GB"
    return GBs_str


def show_last_update(data):
    """Element to display in a page, showing the last update
    by the underlying data storage."""
    t = time.strftime("%c", data.get_last_update())
    return html.Div(f"Data last updated: {t}", id="data-last-update")


def biground(number, base=5):
    """Round a number to the nearest multiple another

    Parameters
    ----------
    number : int
        The number to round.
    base : int, default=5
        The base of which the result will be multiples of

    Returns
    -------
    int
    """
    return base * round(number / base)
