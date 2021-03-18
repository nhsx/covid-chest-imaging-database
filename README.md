# COVID-19 Chest Imaging Database

[NHSX](https://www.nhsx.nhs.uk/) and the [British Society of Thoracic Imaging (BSTI)](https://www.bsti.org.uk/)
have formed a joint partnership in order to create a national database of chest CT, MRI, and X-ray images.
This is to enable the validation and development of automated analysis technologies, and to promote research
projects in response to the COVID-19 pandemic.

This repository contains tooling related to the NHSX National COVID-19 Chest Image Database (NCCID).

## Components

Checks & deployments:

[![Infrastructure](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/infrastructure.yml/badge.svg)](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/infrastructure.yml)
[![Warehouse Loader Checks](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/loader.yml/badge.svg)](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/loader.yml)
[![Docker Image](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/container.yml/badge.svg)](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/container.yml)
[![CodeQL](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/codeql-analysis.yml)

[![Build and Deploy Docs](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/site-deployment.yml/badge.svg)](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/site-deployment.yml)
[![Generate statistics page](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/stats-page.yml/badge.svg)](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/stats-page.yml)
[![Deploy Dashboard](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/dashboard-deploy.yml/badge.svg)](https://github.com/nhsx/covid-chest-imaging-database/actions/workflows/dashboard-deploy.yml)

* [documentation site source code](docs) (docs are deployed [here](https://nhsx.github.io/covid-chest-imaging-database/))
* [infrastructure setup](infrastructure)
* [data warehouse preprocessing and loading tools](warehouse-loader)
* [internal dashboard infrastructure](infrastructure-dashboard) and [dashboard code](dashboard)
