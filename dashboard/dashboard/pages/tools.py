""" Common helper functions for the dashboard pages.

Certain tasks might happen frequently in the dashboard pages
and thus having a central implementation helps eliminating code
duplications where it is possible.
"""


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
