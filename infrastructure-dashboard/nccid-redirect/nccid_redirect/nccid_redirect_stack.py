from aws_cdk import aws_apigatewayv2 as _apigw2
from aws_cdk import aws_apigatewayv2_integrations as _apigw2int
from aws_cdk import aws_certificatemanager as _acm
from aws_cdk import aws_cloudfront as _cloudfront
from aws_cdk import aws_cloudfront_origins as _origins
from aws_cdk import aws_lambda as _lambda
from aws_cdk import core


class NccidRedirectStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Input variables

        # Domain name to redirect
        domain_name = core.CfnParameter(
            self,
            "domainName",
            type="String",
            description="Domain name to redirect",
        )

        # Here we use a specific certificate from parameter values
        cert_arn = core.CfnParameter(
            self,
            "certArn",
            type="String",
            description="Certificate ARN of for the redirection (has to be in us-east-1",
        )
        # End: Input variables

        # Infra setup

        redirect_fn = _lambda.Function(
            self,
            "NCCIDRedirectLambda",
            handler="lambda-handler.handler",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("lambda"),
        )

        redirect_integration = _apigw2int.LambdaProxyIntegration(handler=redirect_fn)

        cert = _acm.Certificate.from_certificate_arn(
            self, "cert", cert_arn.value_as_string
        )

        http_api = _apigw2.HttpApi(
            self,
            "nccid-redirect",
            api_name="nccid-redirect",
            description="A redirection gateway.",
        )

        http_api.add_routes(
            path="/", methods=[_apigw2.HttpMethod.GET], integration=redirect_integration
        )

        origin_target = http_api.url.replace("https://", "", 1)
        origin = _origins.HttpOrigin(domain_name=origin_target)
        behaviour = _cloudfront.BehaviorOptions(origin=origin)

        distribution = _cloudfront.Distribution(  # noqa: F841
            self,
            "nccid-redirect-dist",
            default_behavior=behaviour,
            certificate=cert,
            domain_names=[domain_name.value_as_string],
        )
