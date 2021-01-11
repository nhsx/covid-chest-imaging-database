from werkzeug.middleware.dispatcher import DispatcherMiddleware
from server import create_server

import logging

from pages import register_pages

import time
from timeloop import Timeloop
from datetime import timedelta

from dataset import Dataset
from pathlib import Path
import os

BUCKET = os.getenv("AWS_PROCESSED_BUCKET")
if BUCKET is not None:
    data_latest_path = f"s3://{BUCKET}/latest.csv"
else:
    logging.warning("No bucket name provided via the AWS_PROCESSED_BUCKET env var, trying to load data locally.")
    data_latest_path = Path(__file__).parent / "latest.csv"

data = Dataset(data_latest_path)

server = create_server()
pages = register_pages(data)
# routes = {**component_routes, **example_routes}
routes = {**pages}
application = DispatcherMiddleware(
    server, {slug: app.server for slug, app in routes.items()}
)

tl = Timeloop()

# @tl.job(interval=timedelta(seconds=2))
# def sample_job_every_2s():
#     print("2s job current time : {}".format(time.ctime()))
#     data.inc_counter()
#     print(f"Counter: {data.get_counter()}, {data}")

@tl.job(interval=timedelta(seconds=60))
def sample_job_every_5s():
    print("60s job current time : {}".format(time.ctime()))
    data.load_data()

if __name__ == "__main__":
    import os

    from werkzeug.serving import run_simple

    tl.start(block=False)
    run_simple("localhost", 8888, application, use_reloader=True)
