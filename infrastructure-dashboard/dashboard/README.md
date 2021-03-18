# Dashboard Stack

This folder contains the `AWS CDK`-defined infrastructure of the NCCID dashboard.

## Input variables

The following input variables are defined in the stack code, and require
input at least once for a deploy (on subsequent deploys the previously
set values are automatically reused for any missing input variable).

* `certArn`: The SSL certificate to use. Create a certificate for the
  desired domain (that will be redirected), making sure the certificate
  is in the `us-east-1` zone (required by CloudFront). This might need
  coordination with the DNS administrator of the domain, to allow validation.
  Wait until the certificate is validated, and grab it's ARN.
* `domainName`: the domain name that the above certificate is created for
  (required by CloudFront)
* `processedBucket`: the name of the S3 bucket where the preprocessed warehouse
  data is pushed to. The dashboard will download the preprocessed data from there.
* `imageTag`: the relevant tag of of the Docker image to deploy in the
  ECR repository created by the stack (default name of the registry
  is as defined in the code, here `nccid-dashboard`). If images are manually
  created, this is the repository to push to (following e.g. the guidance
  in th AWS console on how to do the image push).
* `cookieSecret`: a suitably long random string to use as cookie secret with
  the dashboard authentication. If changed, any dashboard user who was logged
  in has to clear their cookies before trying to re-login, otherwise might
  end up having some cryptic error messages. Thus it's useful not to change
  this value, unless necessary to reset all the cookies.

## Configuration outside of this stack

The deployed stack will emit a variable called `nccid-dashboard.nccidCloudfrontDistribution`,
which is the deployed CloudFront distribution serving the dashboard.
On the domain DNS management side you have to set the `CNAME` value
for the domain passed in as `domainName` to this CloudFront distribution
value.


# Welcome to your CDK Python project!

You should explore the contents of this project. It demonstrates a CDK app with an instance of a stack (`dashboard_stack`)
which contains an Amazon SQS queue that is subscribed to an Amazon SNS topic.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization process also creates
a virtualenv within this project, stored under the .venv directory.  To create the virtualenv
it assumes that there is a `python3` executable in your path with access to the `venv` package.
If for any reason the automatic creation of the virtualenv fails, you can create the virtualenv
manually once the init process completes.

To manually create a virtualenv on MacOS and Linux, use for example:

```shell
python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```shell
source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```shell
.venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```shell
pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```shell
cdk synth
```

You can now begin exploring the source code, contained in the [`dashboard`](dashboard)
directory.

Then to move towards deployment, authenticate to AWS and set the relevant credentials in
environment variables (or use [`aws-vault`](https://github.com/99designs/aws-vault)
to manage these for you)

To see the differences of any modifications you make, compared to the currently
deployed stack, you can issue the `diff` command:

```shell
$ cdk diff
Stack nccid-dashboard
There were no differences
```

Note that this difference doesn't take into account any input parameter values
that might affect any deployment, just the generic, pre-parameter infrastructure.

To deploy, run the `deploy` command with the appropriate flags, with the
parameters filled out with their actual values:

```shell
cdk deploy --parameters certArn=CERTIFICATE_ARN \
           --parameters domainName=DOMAIN_NAME \
           --parameters processedBucket=PROCESSED_BUCKET_NAME \
           --parameters imageTag=IMAGE_TAG \
           --parameters cookieSecret=COOKIE_SECRET
```

Since the CloudFormation stack keeps track of existing parameter values,
to reuse the previous values, you can choose to define only the values
that have changed, or if nothing has changed for the parameters, you can
just run the command without any `--parameters` flagas.

```shell
$ cdk deploy
nccid-dashboard: deploying...
nccid-dashboard: creating CloudFormation changeset...


 ✅  nccid-dashboard

Outputs:
nccid-dashboard.DashboardServiceLoadBalancerABCD1234 = <redacted>
nccid-dashboard.nccidCloudfrontDistribution = <redacted>

Stack ARN:
arn:aws:cloudformation:<redacted>
```

## Useful CDK commands

* `cdk ls`          list all stacks in the app
* `cdk synth`       emits the synthesized CloudFormation template
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk docs`        open CDK documentation

## GitHub Action

This stack can be deployed both manually or using a [GitHub Action](https://github.com/features/actions)
automatically. The action uses 3rd party developed CDK actions at the moment, and
requires a number of [secrets](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets)
to be set.

* `AWS_KEY_ID`: the key ID of a set of credentials for an AWS IAM user that is used to deploy the stack in the action
* `AWS_SECRET_ACCESS_KEY`: the secret part of the key
* `AWS_DASHBOARD_CERTIFICATE_ARN`: the HTTPS certificate to use
* `DASHBOARD_DOMAIN`: the domain to set up (it should be covered by the certificate above)

### Deployment permissions

To deploy this stack as a GitHub Action, the associated IAM user/key will have to
have at least these permissions (possibly more)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "GeneralResources",
            "Effect": "Allow",
            "Action": [
                "iam:GetRole",
                "iam:PassRole",
                "cloudfront:*",
                "secretsmanager:*",
                "logs:*",
                "ecs:*",
                "ec2:*",
                "iam:CreateRole",
                "iam:DeleteRole",
                "ecr:*",
                "elasticloadbalancing:*",
                "iam:PutRolePolicy"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CloudformationAllow",
            "Effect": "Allow",
            "Action": "cloudformation:*",
            "Resource": [
                "<Deployed CloudFormation Stack ARN>",
                "<CDKToolkit CloudFormation Stack ARN>"
            ]
        },
        {
            "Sid": "CloudformationDeny",
            "Effect": "Deny",
            "Action": "cloudformation:DeleteStack",
            "Resource": [
                "<Deployed CloudFormation Stack ARN>",
                "<CDKToolkit CloudFormation Stack ARN>"
            ]
        }
    ]
}
```

where the `<Deployed CloudFormation Stack ARN>` and `<CDKToolkit CloudFormation Stack ARN>`
values need to inserted. (Alternatively allow all Cloudformation resources as well in the
first block).

Likely some other `iam:` actions need whitelisting as well, but this is the currently
best knowledge.
