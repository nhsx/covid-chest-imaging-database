# NCCID Dashboard

A dashboard to view metrics and information about the NCCID dataset.

## Development

Make sure you install the Python package requirements with

```Shell
pip install -r requirements.txt
```

You'll need to set up an [Okta](https://www.okta.com/) application,
that will provide the authentication for the locally running site.

Once signed up for Okta, create a new "OpenID Application". In the
application control panel:

* enable `Authorization Code` for the`Allowed grant types` field,
* fill in the `Login redirect URIs` and `Logout redirect URIs`. The values
  of that depends on how you run the application, and might need to
  update it occasionally. Example values to fill in are given further
  in this document.
* make a note of the `Okta domain`, `Client ID` and `Client secret` values,
  as you'll need to fill those in on the server side.

Other requirements include access to the data to be displayed. This can be
a local cache of CSV files, or access to a remote S3 bucket that have the
relevant data.

For local cache, you'll need a `latest.csv` file that points to the specific
data CSV archives, for example:

```Csv
archive,path
ct,ct.csv
mri,mri.csv
xray,xray.csv
patient_clean,patient_clean.csv
```
and then having the `ct.csv`, `xray.csv`, `mri.csv`, `patient_clean.csv`
in the local folder.

For remote access, have to expose AWS credentials as environment variables
and set the `AWS_PROCESSED_BUCKET` environment variable to contain the bucket
name from where the `latest.csv` and all the other files can be loaded from.

### Running locally

For local run:

* `Login redirect URIs` should have an entry of `http://localhost:8888/authorization-code/callback`
* `Logout redirect URIs` should have an entry of `http://localhost:8888`
* should copy `env.template` to `.env` in the same folder, and fill in the
  `Okta domain`, `Client ID` and `Client secret` values as appropriate.

Then start up the server with:

```shell
COOKIE_INSECURE=yes FLASK_ENV=development python run.py
```

Navigate to [http://localhost:8888](http://localhost:8888) to view the server.
On code change Flask will automatically reload the server.

### Running on Faculty Platform

Start a new interactive server, and "open server" to get the name of the server you
are working with (`https://cube-...`).

* `Login redirect URIs` should have an entry of `https://cube-.../authorization-code/callback`
  where the cube name is completely filled in.
* `Logout redirect URIs` should have an entry of `https://cube-...`, where the cube name is
  completely filled in.
* should copy `env.template` to `.env` in the same folder, and fill in the
  `Okta domain`, `Client ID` and `Client secret` values as appropriate.

Then start up the server with:

```shell
DASHBOARD_DOMAIN=cube-... FLASK_ENV=development python run.py
```
where the `DASHBOARD_DOMAIN` is the domain name of the cube (without the starting `https://`).

Then navigate to that domain (or "open server"), and see the dashboard running.
