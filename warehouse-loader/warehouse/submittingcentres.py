""" This module helps extracting the submitting centres from
the uploaded raw dataset.
"""

import logging
from pathlib import Path

import bonobo
import mondrian
from bonobo.config import Configurable, ContextProcessor, use_raw_input
from bonobo.util.objects import ValueHolder

import warehouse.warehouseloader as wl  # noqa: E402
from warehouse.components.services import (
    Inventory,
    PipelineConfig,
    SubFolderList
)

mondrian.setup(excepthook=True)
logger = logging.getLogger()


class SubmittingCentreExtractor(Configurable):
    """ Get unique submitting centre names from the full database.
    """

    @ContextProcessor
    def acc(self, context):
        centres = yield ValueHolder(set())
        for centre in sorted(centres.get()):
            print(centre)

    @use_raw_input
    def __call__(self, centres, *args, **kwargs):
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

    :return: bonobo.Graph
    """
    graph = bonobo.Graph()

    graph.add_chain(
        wl.load_config,
        wl.extract_raw_folders,
        wl.extract_raw_files_from_folder,
        SubmittingCentreExtractor(),
    )

    return graph


def get_services(**options):
    """
    This function builds the services dictionary, which is a simple dict of names-to-implementation used by bonobo
    for runtime injection.

    It will be used on top of the defaults provided by bonobo (fs, http, ...). You can override those defaults, or just
    let the framework define them. You can also define your own services and naming is up to you.

    :return: dict
    """
    config = PipelineConfig()
    rawsubfolderlist = SubFolderList(folder_list=["data/"])
    # Do not use inventory in this task as it is already quite fast
    inventory = Inventory()

    return {
        "config": config,
        "rawsubfolderlist": rawsubfolderlist,
        "inventory": inventory,
    }


def main():
    """Execute the pipeline graph
    """
    parser = bonobo.get_argument_parser()
    with bonobo.parse_args(parser) as options:
        bonobo.run(get_graph(**options), services=get_services(**options))


# The __main__ block actually execute the graph.
if __name__ == "__main__":
    main()
