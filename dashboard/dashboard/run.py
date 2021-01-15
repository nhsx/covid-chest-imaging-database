"""The NCCID dashboard server runner
"""

import logging
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from timeloop import Timeloop

from dataset import Dataset
from pages import register_pages
from server import create_server

load_dotenv()

BUCKET = os.getenv("AWS_PROCESSED_BUCKET")
if BUCKET is not None:
    data_latest_path = f"s3://{BUCKET}/latest.csv"
else:
    logging.warning(
        "No bucket name provided via the AWS_PROCESSED_BUCKET env var. "
        + "Trying to load data locally."
    )
    data_latest_path = str(Path(__file__).parent / "latest.csv")

data = Dataset(data_latest_path)

server, oidc = create_server()
register_pages(data, server)

# Add authentication requirements for all dashboard pages
for view_func in server.view_functions:
    if view_func.startswith("/pages/"):
        server.view_functions[view_func] = oidc.require_login(
            server.view_functions[view_func]
        )

tl = Timeloop()


@tl.job(interval=timedelta(hours=4))
def reload_data():
    server.logger.info("Periodic data reload starting.")
    data.load_data()


if __name__ == "__main__":
    import os

    from werkzeug.serving import run_simple

    tl.start(block=False)
    run_simple("localhost", 8888, server, use_reloader=True)
