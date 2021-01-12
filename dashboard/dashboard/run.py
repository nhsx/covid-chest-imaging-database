"""The NCCID dashboard server runner
"""

import logging
import os

# from datetime import timedelta
from pathlib import Path

from timeloop import Timeloop

from dataset import Dataset
from pages import register_pages
from server import create_server

# from werkzeug.middleware.dispatcher import DispatcherMiddleware


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
# routes = {**component_routes, **example_routes}
# routes = {**pages}
# routes = {}
# application = DispatcherMiddleware(
#     server, {slug: app.server for slug, app in routes.items()}
# )
# application = DispatcherMiddleware(
#     server, {}
# )

# Add authentication requirements for all dashboard pages
for view_func in server.view_functions:
    if view_func.startswith("/pages/"):
        server.view_functions[view_func] = oidc.require_login(
            server.view_functions[view_func]
        )

tl = Timeloop()

# Set up recurring jobs
# @tl.job(interval=timedelta(seconds=2))
# def sample_job_every_2s():
#     print("2s job current time : {}".format(time.ctime()))
#     data.inc_counter()
#     print(f"Counter: {data.get_counter()}, {data}")

# @tl.job(interval=timedelta(seconds=60))
# def sample_job_every_5s():
#     print("60s job current time : {}".format(time.ctime()))
#     data.load_data()

if __name__ == "__main__":
    import os

    from werkzeug.serving import run_simple

    tl.start(block=False)
    run_simple("localhost", 8080, server, use_reloader=True)
