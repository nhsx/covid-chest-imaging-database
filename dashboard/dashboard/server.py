from flask import Flask, abort, redirect, render_template, url_for
from flask_oidc import OpenIDConnect
from jinja2 import TemplateNotFound


def create_server():
    """Create the main Flask server of the dashboard, including
    authentication
    """
    server = Flask(__name__)

    server.config.update(
        {
            "SECRET_KEY": "HmZat4D6S3cGv6mbdTFm",
            # Create this clients_secret from the environment (as an in-memory file?)
            "OIDC_CLIENT_SECRETS": "./client_secrets.json",
            # This should be false in local testing but always true in production
            "OIDC_ID_TOKEN_COOKIE_SECURE": not server.debug,
            "OIDC_SCOPES": ["openid", "profile"],
            "OIDC_CALLBACK_ROUTE": "/authorization-code/callback",
        }
    )

    oidc = OpenIDConnect(server)

    @server.route("/")
    def index():
        if oidc.user_loggedin:
            return redirect(url_for("pages"))
        else:
            try:
                return render_template("index.html")
            except TemplateNotFound:
                abort(404)

    @server.route("/login")
    @oidc.require_login
    def login():
        # return render_template("login.html")
        return redirect(url_for("pages"))

    @server.route("/logout", methods=["POST"])
    def logout():
        oidc.logout()
        return redirect(url_for("index"))

    @server.route("/pages")
    @oidc.require_login
    def pages():
        return redirect("/pages/summary", 302)


    def _oidc_error(message='Not Authorized', code=None):
        try:
            return render_template("index.html", alert=message)
        except TemplateNotFound:
            abort(404)
    oidc._oidc_error = _oidc_error

    return server, oidc
