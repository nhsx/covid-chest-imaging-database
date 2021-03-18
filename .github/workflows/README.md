# GitHub Actions / Automation

This folder contains the GitHub Actions defined for the repository.
they fall into a couple of different categories:

## Testing and linting

These tasks are mainly about running tests and linting check on
some part of the warehouse:

* `codeql-analysis.yml`: GitHub Security Lab's [CodeQL](https://securitylab.github.com/tools/codeql)
  analysis run on the repository, to find any unexpected issues.
* `container.yml`: checks run on all the Docker container definitions in this code for best practices,
  using [hadolint](https://github.com/hadolint/hadolint).
* `infrastructure.yml`: checks run on the infrastructure CloudFormation templates using [cfn-lint](https://github.com/aws-cloudformation/cfn-python-lint).
* `loader.yml`: running linting and tests of the warehouse loading pipeline

## Deployment

These tasks take care of automatic deployment of different parts of the projects:

* `dashboard-deploy.yml`: building the dashboard Docker image and deploying the updated infrastructure,
  using [AWS CDK](https://docs.aws.amazon.com/cdk/)
* `site-deployment.yml`: building and deploying the project website from the docs to GitHub Pages.
* `site-preview.yml`: building and deploying the project website from a PR to an S3 bucket, and making
  it available as GitHub Deployment inside the PR to quickly view the results.

## Periodic tasks / automation

* `stats-page.yml`: automatic recalculation of the training set statistic on the website on a regular
  schedule, and opening PRs based on the changes.
