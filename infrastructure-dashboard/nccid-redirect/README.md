# NCCID Redirection stack

## Prerequisites

Create a certificate for the desired domain (that will be redirected), making
sure the certificate is in the `us-east-1` zone (required by Cloudfront).

Wait until the certificate is validated, and grab it's ARN.

The domain name and the certificate ARN are the two inputs for the redirection
stack deployed in the next step.
## How to use the CDK deployment

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

Next, export your AWS credentials to your shell, or if using
[aws-vault](https://github.com/99designs/aws-vault), run:
```
$ aws-vault exec <profile> --no-session
```
as the deployment will require IAM changes that doesn't work with session tokens.

To deploy the stack, you might first need to bootstrap your environment:
```
$ cdk bootstrap
```
which will create the relevant S3 bucket in your default region.

Then run the following deploy command, replacing `<CERITFICATE_ARN>` and `<DOMAIN_NAME>` with
the relevant values:

```
$ cdk deploy --parameters certArn=<CERTIFICATE_ARN> --parameters domainName=<DOMAIN_NAME>
```

At the end you should get an output of a Cloudfront distribution domain (), that you
need to set as the target of the `CNAME` setting of the `<DOMAIN_NAME>`:

```
[...snip...]
Outputs:
nccid-redirect.nccidRedirectDomain = <redacted>.cloudfront.net
```
