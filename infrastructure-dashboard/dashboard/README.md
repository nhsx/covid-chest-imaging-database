
# Welcome to your CDK Python project!

You should explore the contents of this project. It demonstrates a CDK app with an instance of a stack (`dashboard_stack`)
which contains an Amazon SQS queue that is subscribed to an Amazon SNS topic.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization process also creates
a virtualenv within this project, stored under the .venv directory.  To create the virtualenv
it assumes that there is a `python3` executable in your path with access to the `venv` package.
If for any reason the automatic creation of the virtualenv fails, you can create the virtualenv
manually once the init process completes.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

You can now begin exploring the source code, contained in the hello directory.
There is also a very trivial test included that can be run like this:

```
$ pytest
```

To add additional dependencies, for example other CDK libraries, just add to
your requirements.txt file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!


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
