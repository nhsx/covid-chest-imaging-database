from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_apigatewayv2 as _apigw2,
    aws_apigatewayv2_integrations as _apigw2int,
    aws_certificatemanager as _acm,
)


class NccidRedirectStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        domain_name = core.CfnParameter(
            self,
            "domainName",
            type="String",
            description="Domain name to redirect",
        )

        redirect_fn = _lambda.Function(
            self,
            "NCCIDRedirectLambda",
            handler="lambda-handler.handler",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset("lambda"),
        )

        redirect_integration = _apigw2int.LambdaProxyIntegration(handler=redirect_fn)

        ## Could do our own certificate, if we were to control the DNS settings ourselves.
        # cert = _acm.Certificate(
        #     self,
        #     id="nccid-redirection",
        #     domain_name=domain_name.value_as_string,
        #     validation=_acm.CertificateValidation.from_dns(),
        # )

        # Here we use a specific certificate from paramter values
        cert_arn = core.CfnParameter(
            self,
            "certArn",
            type="String",
            description="Certificate ARN of for the redirection",
        )
        cert = _acm.Certificate.from_certificate_arn(
            self, "cert", cert_arn.value_as_string
        )

        dn = _apigw2.DomainName(
            self,
            "nccid-redirect-domain",
            domain_name=domain_name.value_as_string,
            certificate=cert,
        )

        http_api = _apigw2.HttpApi(
            self,
            "nccid-redirect",
            api_name="nccid-redirect",
            description="A redirection gateway.",
            default_domain_mapping={"domain_name": dn},
        )

        http_api.add_routes(
            path="/", methods=[_apigw2.HttpMethod.GET], integration=redirect_integration
        )
