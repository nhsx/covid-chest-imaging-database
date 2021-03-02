import json
import logging
import re

import mondrian
from botocore.exceptions import ClientError

# set up logging
mondrian.setup(excepthook=True)
logger = logging.getLogger()


def get_date_from_key(key):
    """Extract date from an object key from the bucket's directory pattern,
    for a given prefix

    Parameters
    ----------
    key : str
        the object key in question

    Returns
    -------
    str or None
        The extracted date if found, in YYYY-MM-DD format
    """
    date_match = re.match(r"^.+/(?P<date>\d{4}-\d{2}-\d{2})/.+", key)
    if date_match:
        return date_match.group("date")


def get_submitting_centre_from_key(s3client, key):
    """Extract the SubmittingCentre value from an S3 object that is
    a JSON file in the expected format.

    Parameters
    ----------
    obj : boto3.resource('s3').ObjectSummary
        The S3 object of the JSON file to process.

    Returns
    -------
    str or None
        The value defined for the SubmittingCentre field in the file
    """
    try:
        file_content = s3client.object_content(key).decode("utf-8")
        json_content = json.loads(file_content)
    except ClientError:
        logger.error(f"Couldn't download contents of {key}.")
        raise
    except json.decoder.JSONDecodeError:
        logger.error(f"Couldn't decode contents of {key} as JSON. ")
        raise
    return json_content.get("SubmittingCentre")
