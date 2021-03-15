# National COVID-19 Chest Image Database (NCCID) Documentation / Website

This [Sphinx](https://www.sphinx-doc.org/en/master/) based documentation contains
the source code of the website [deployed to GitHub Pages](https://nhsx.github.io/covid-chest-imaging-database/).

## Build the site locally

Install the required Python dependencies

```shell
pip install -r requirements.txt
```

and run the build with:

```shell
make html
```

If the site has already been built locally, you might want to clean the existing
data and regenerate everything.

```shell
make clean & make html
```

## Deployment (testing and production)

All pull requests (PR) are deployed with a GitHub Action to S3 as a website, using GitHub
"deployments". When a PR is made [this workflow](../.github/workflows/site-preview.yml)
will attempt to generate the pages, and upload them to a public S3 bucket that exists
for this purpose. The automation then will show a "deployment" on the PR itself,
which can be clicked and the site previewed. Note: for this to work the PR has to be
up-to-date with the master branch. See the [infrastructure README](../infrastructure/README.md)
for more info on the S3 bucket.

Commits merged to master are automatically deployed using the GitHub Actions / GitHub Pages
setup, using [this workflow](../.github/workflows/site-deployment.yml).
