""" This module helps extracting the submitting centres from
the uploaded raw dataset.
"""

import logging
import os
import re
from pathlib import Path

import bonobo
import mondrian
from bonobo.config import (
    Configurable,
    ContextProcessor,
    Service,
    use,
    use_raw_input,
)
from bonobo.util.objects import ValueHolder

import warehouse.components.helpers as helpers
import warehouse.warehouseloader as wl  # noqa: E402
from warehouse.components.services import (
    FileList,
    InventoryDownloader,
    PipelineConfig,
    S3Client,
)

mondrian.setup(excepthook=True)
logger = logging.getLogger()

BUCKET_NAME = os.getenv("WAREHOUSE_BUCKET", default=None)
NO_OUTPUT_FILE = bool(os.getenv("NO_OUTPUT_FILE", default=False))


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
    for key in filelist.get_raw_data_list(raw_prefixes=raw_prefixes):
        key_match = pattern.match(key)
        if key_match and key_match.group("pseudonym") not in donelist:
            donelist.add(key_match.group("pseudonym"))
            yield "process", key, None


class SubmittingCentreExtractor(Configurable):
    """Get unique submitting centre names from the full database."""

    s3client = Service("s3client")

    @ContextProcessor
    def acc(self, context, **kwargs):
        centres = yield ValueHolder(set())
        for centre in sorted(centres.get()):
            print(centre)
        if not NO_OUTPUT_FILE:
            with open("/tmp/message.txt", "w") as f:
                for centre in sorted(centres.get()):
                    print(centre, file=f)

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
        task, key, _ = args
        s3client = kwargs["s3client"]
        if task == "process" and Path(key).suffix.lower() == ".json":
            centre, patient_group = helpers.get_split_info_from_key(
                s3client, key
            )
            # Only add the centre to the output list if PatientGroup is not set,
            # since otherwise it won't need to be added to the
            if patient_group is None and centre is not None:
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
    if BUCKET_NAME is None:
        return {
            "config": None,
            "filelist": None,
            "s3client": None,
        }

    config = PipelineConfig()
    inv_downloader = InventoryDownloader(main_bucket=BUCKET_NAME)
    filelist = FileList(inv_downloader)
    s3client = S3Client(bucket=BUCKET_NAME)

    return {
        "config": config,
        "filelist": filelist,
        "s3client": s3client,
    }


def main():
    """Execute the pipeline graph"""
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**options), services=get_services(**options))


# The __main__ block actually execute the graph.
if __name__ == "__main__":
    main()
