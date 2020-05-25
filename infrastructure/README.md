# Infrastructure

This folder contains the relevant infrastructure setup for the
NCCID warehouse, and for this repository:

The `templates` folder hosts the [CloudFormation](https://aws.amazon.com/cloudformation/)
templates, while the Python scripts are used for applying those templates.

## Warehouse

The docs previews for this repository are stored in an S3 bucket,
which is created from the [`warehouse.yaml`](templates/warehouse.yaml)
template.

```shell
$ ./create.py --help
INFO:botocore.credentials:Found credentials in environment variables.
usage: create.py [-h] [-s SUFFIX]

optional arguments:
  -h, --help            show this help message and exit
  -s SUFFIX, --suffix SUFFIX
                        suffix to use for templates and names
```


## Docs Preview

The docs previews for this repository are stored in an S3 bucket,
which is created from the [`docs-preview.yaml`](templates/docs-preview.yaml)
template. Use the `docs-preview.py` script (with the AWS credentials set
in the environment) to create or update the CloudFormation stack

```shell
$ ./docs-preview.py --help
INFO:botocore.credentials:Found credentials in environment variables.
usage: docs-preview.py [-h] [-b BUCKET]

optional arguments:
  -h, --help            show this help message and exit
  -b BUCKET, --bucket BUCKET
                        The docs preview bucket's name
```

The Preview workflow uses this bucket. You need to create an AWS programmatic
user, add it to the relevant `docs-preview-....-DocsPreviewUploaderGroup-...` group.
Finally, you need to set these GitHub Secrets:

* `AWS_DOCS_PREVIEW_BUCKET`: the name of the bucket, such as `nhsx-covid-chest-imaging-database-preview`
* `AWS_DOCS_PREVIEW_BUCKET_REGION`: the region of the bucket, such as `eu-west-2`
* `AWS_KEY_ID`: credential ID for the relevant AWS user created for the GitHub Action
* `AWS_SECRET_ACCESS_KEY`: credential value for the relevant AWS user created for the GitHub Action
