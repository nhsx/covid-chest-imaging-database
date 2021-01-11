from werkzeug.middleware.dispatcher import DispatcherMiddleware
from server import create_server

from pages import register_pages

import time
from timeloop import Timeloop
from datetime import timedelta

from dataset import Dataset



data = Dataset()

server = create_server()
# component_routes = register_component_apps()
pages = register_pages(data)
# routes = {**component_routes, **example_routes}
routes = {**pages}
application = DispatcherMiddleware(
    server, {slug: app.server for slug, app in routes.items()}
)

tl = Timeloop()



@tl.job(interval=timedelta(seconds=2))
def sample_job_every_2s():
    print("2s job current time : {}".format(time.ctime()))
    data.inc_counter()
    print(f"Counter: {data.get_counter()}, {data}")

@tl.job(interval=timedelta(seconds=60))
def sample_job_every_5s():
    print("5s job current time : {}".format(time.ctime()))
    data.inc_counter(step=100)

if __name__ == "__main__":
    import os

    from werkzeug.serving import run_simple

    os.environ["DBC_DOCS_MODE"] = "dev"
    tl.start(block=False)
    run_simple("localhost", 8888, application, use_reloader=True)