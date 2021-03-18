#!/usr/bin/env python

import argparse
from datetime import datetime

import boto3
from tqdm.auto import tqdm

client = boto3.client("logs")


def get_latest_stream_name(log_group_name):
    """Get the latest stream name for a given log group

    Parameters
    ----------
    log_group_name : str
        The name of the log group to query for streams.

    Returns
    -------
    str
        The name of the latest log stream in the log group
    """
    response = client.describe_log_streams(
        logGroupName=log_group_name,
        orderBy="LastEventTime",
        descending=True,
        limit=1,
    )
    return response["logStreams"][0]["logStreamName"]


def get_logs(
    log_stream_name, log_group_name, forward_token=None,
):
    """
    Get the logs for a given log stream, optionally using 
    a forward continuation token.

    Parameters
    ----------
    log_stream_name : str
        The name of the log stream to query
    log_group_name : str
        The log group that the stream belongs to
    forward_token : str or None,default=None
        The forward continuation token extracted from an earlier response

    Returns
    -------
    dict
        Log events as returned by boto, for more details
        see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_log_events
    """
    kwargs = {
        "logGroupName": log_group_name,
        "logStreamName": log_stream_name,
        "startFromHead": True,
    }
    if forward_token is not None:
        kwargs["nextToken"] = forward_token
    return client.get_log_events(**kwargs)


if __name__ == "__main__":
    # Arguments setup
    parser = argparse.ArgumentParser(description="Get a whole log stream with all the fragments from AWS.")
    parser.add_argument(
        "-g",
        "--group-name",
        help="The name of the log group to use.",
        default="/ecs/warehouse-prod-pipeline",
    )
    parser.add_argument(
        "-s",
        "--stream-name",
        help="The log stream name to get. "
        + "By default the latest stream is queried and downloaded.",
    )
    parser.add_argument(
        "-o", "--output-file", help="File to save the log results to.",
    )
    args = parser.parse_args()
    # End arguments setup

    stream_name = (
        get_latest_stream_name(log_group_name=args.group_name)
        if args.stream_name is None
        else args.stream_name
    )

    f = open(args.output_file, "w") if args.output_file else None
    print_kwargs = {"file": f} if f is not None else {}

    forward_token = None
    # Display progress bar
    pbar = tqdm(desc="Gathering log fragments", unit="piece")
    while True:
        result = get_logs(
            stream_name,
            log_group_name=args.group_name,
            forward_token=forward_token,
        )
        pbar.update(1)
        count = len(result["events"])
        if count == 0:
            pbar.close()
            break

        forward_token = result["nextForwardToken"]
        for event in result["events"]:
            timestamp = datetime.fromtimestamp(event["timestamp"] / 1000)
            message = event["message"]
            print(f"{timestamp.isoformat()} {message}", **print_kwargs)

    if f is not None:
        f.close()
