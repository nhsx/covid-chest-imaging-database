from flask import Flask, abort, redirect, render_template
from jinja2 import TemplateNotFound

def create_server():
    server = Flask(__name__)

    @server.route("/")
    def index():
        try:
            return render_template("index.html")
        except TemplateNotFound:
            abort(404)

    @server.route("/pages")
    def components_index():
        return redirect("/pages/summary", 302)

    return server
