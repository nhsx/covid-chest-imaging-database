# National COVID-19 Chest Image Database (NCCID) Documentation / Website

This [Next.js](https://nextjs.org/docs) based documentation contains
the source code of the website [deployed to GitHub Pages](https://nhsx.github.io/covid-chest-imaging-database/).

## Build the site locally

First, run the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

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

## Statistics

The statistics are automatically generated on a weekly bases and stored in the `/docs/public/data` folder.

The hospital locations are also placed here but are updated manually. 

## Content

Content is stored in MDX format and can be found in `/docs/documentation`. To make a change, create a new PR with the required changes. 