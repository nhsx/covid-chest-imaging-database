import json
import os

from flask import Flask, abort, redirect, render_template, url_for
from flask_oidc import OpenIDConnect
from jinja2 import TemplateNotFound


def config_prepare():
    if os.environ.get("0") is not None:
        secrets = json.loads(os.environ.get("0"))
        client_secrets = generate_oidc_client_secrets(secrets)
        oidc_client_secrets = "./client_secrets.auto.json"
        with open(oidc_client_secrets, "w") as secrets_fp:
            json.dump(client_secrets, secrets_fp)
        json.dumps(client_secrets)
    else:
        oidc_client_secrets = "./client_secrets.json"

    cookie_secret_key = os.environ.get(
        "COOKIE_SECRET_KEY", "NotVerySecretBecauseNotSet"
    )
    cookie_secure = False if os.environ.get("COOKIE_INSECURE") else True

    config = {
        "SECRET_KEY": cookie_secret_key,
        "OIDC_CLIENT_SECRETS": oidc_client_secrets,
        "OIDC_ID_TOKEN_COOKIE_SECURE": cookie_secure,
        "OIDC_SCOPES": ["openid", "profile"],
        "OIDC_CALLBACK_ROUTE": "/authorization-code/callback",
    }
    return config


def generate_oidc_client_secrets(secrets):
    web = {
        "auth_uri": f"https://{secrets['okta_auth_domain']}/oauth2/default/v1/authorize",
        "client_id": secrets["okta_client_id"],
        "client_secret": secrets["okta_client_secret"],
        "redirect_uris": [
            "http://localhost:8080/authorization-code/callback",
        ],
        "issuer": f"https://{secrets['okta_auth_domain']}/oauth2/default",
        "token_uri": f"https://{secrets['okta_auth_domain']}/oauth2/default/v1/token",
        "token_introspection_uri": f"https://{secrets['okta_auth_domain']}/oauth2/default/v1/introspect",
        "userinfo_uri": f"https://{secrets['okta_auth_domain']}/oauth2/default/v1/userinfo",
    }
    return {"web": web}


def create_server():
    """Create the main Flask server of the dashboard, including
    authentication
    """
    server = Flask(__name__)

    config_update = config_prepare()

    server.config.update(config_update)

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
        return redirect(url_for("pages"))

    @server.route("/logout", methods=["POST"])
    def logout():
        oidc.logout()
        return redirect(url_for("index"))

    @server.route("/pages")
    @oidc.require_login
    def pages():
        return redirect("/pages/summary", 302)

    def _oidc_error(message="Not Authorized", code=None):
        try:
            return render_template("index.html", alert=message)
        except TemplateNotFound:
            abort(404)

    oidc._oidc_error = _oidc_error

    return server, oidc
