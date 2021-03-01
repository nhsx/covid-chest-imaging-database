""" This module helps extracting the submitting centres from
the uploaded raw dataset.
"""

import logging
import os
import re
from pathlib import Path

import bonobo
import mondrian
from bonobo.config import Configurable, ContextProcessor, use, use_raw_input
from bonobo.util.objects import ValueHolder

import warehouse.warehouseloader as wl  # noqa: E402
from warehouse.components.services import (
    FileList,
    InventoryDownloader,
    PipelineConfig,
)

mondrian.setup(excepthook=True)
logger = logging.getLogger()

BUCKET_NAME = os.getenv("WAREHOUSE_BUCKET", default="chest-data-warehouse")


@use("config")
@use("filelist")
def extract_raw_data_files(config, filelist):
    """Extract files from a given date folder in the data dump

    Parameters
    ----------
    config : PipelineConfig
        A configuration store.
    filelist : FileList
        To get the relevant file lists from the inventory.

    Yields
    ------
    tuple[str, boto3.resource('s3').ObjectSummary, None]
        A task name ("process"), object to process, and a placeholder value
    """
    raw_prefixes = {prefix.rstrip("/") for prefix in config.get_raw_prefixes()}
    pattern = re.compile(
        r"^raw-.*/\d{4}-\d{2}-\d{2}/data/(?P<pseudonym>[^/]*)_(data|status).json$"
    )
    donelist = set()
    # List the clinical data files for processing
    for obj in filelist.get_raw_data_list(raw_prefixes=raw_prefixes):
        key_match = pattern.match(obj.key)
        if key_match and key_match.group("pseudonym") not in donelist:
            donelist.add(key_match.group("pseudonym"))
            yield "process", obj, None


class SubmittingCentreExtractor(Configurable):
    """Get unique submitting centre names from the full database."""

    @ContextProcessor
    def acc(self, context):
        centres = yield ValueHolder(set())
        for centre in sorted(centres.get()):
            print(centre)

    @use_raw_input
    def __call__(self, centres, *args, **kwargs):
        """The accumulator fuction run by the pipeline.

        Parameters
        ----------
        centres : ValueHolder(set())
            Accumulator for the centre names
        task, obj, _ = tuple[str, boto3.resource('s3').ObjectSummary, None]
            A task name ("process" is what accepted here) and a clinical data file
            object to extract the submitting centre from.
        **kwargs : dict
            Keyword arguments.
        """
        task, obj, _ = args
        if task == "process" and Path(obj.key).suffix.lower() == ".json":
            centre = wl.get_submitting_centre_from_object(obj)
            if centre is not None:
                centres.add(centre)


###
# Graph setup
###
def get_graph(**options):
    """
    This function builds the graph that needs to be executed.

    Parameters
    ----------
    **options : dict
        Keyword arguments.

    Returns
    -------
    bonobo.Graph
        The assembled processing graph.
    """
    graph = bonobo.Graph()

    graph.add_chain(
        wl.load_config,
        extract_raw_data_files,
        SubmittingCentreExtractor(),
    )

    return graph


def get_services(**options):
    """
    This function builds the services dictionary, which is a simple dict of names-to-implementation used by bonobo
    for runtime injection.

    It will be used on top of the defaults provided by bonobo (fs, http, ...). You can override those defaults, or just
    let the framework define them. You can also define your own services and naming is up to you.

    Returns
    -------
    dict
        Mapping of service names to objects.
    """
    config = PipelineConfig()
    inv_downloader = InventoryDownloader(main_bucket=BUCKET_NAME)
    filelist = FileList(inv_downloader)

    return {
        "config": config,
        "filelist": filelist,
    }


def main():
    """Execute the pipeline graph"""
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**options), services=get_services(**options))


# The __main__ block actually execute the graph.
if __name__ == "__main__":
    main()
