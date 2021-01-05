from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_ecs_patterns as ecs_patterns,
    aws_certificatemanager as _acm,
    aws_cloudfront as _cloudfront,
    aws_cloudfront_origins as _origins,
    aws_secretsmanager as secretsmanager,
    core,
)


class DashboardStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Domain name to redirect
        domain_name = core.CfnParameter(
            self, "domainName", type="String", description="Domain name to redirect",
        )

        # Here we use a specific certificate from parameter values
        cert_arn = core.CfnParameter(
            self,
            "certArn",
            type="String",
            description="Certificate ARN of for the redirection (has to be in us-east-1",
        )

        image_tag = core.CfnParameter(
            self,
            "imageTag",
            type="String",
            description="Image tag to deploy as container",
        )
        # End: Input variables

        # Create VPC and Fargate Cluster
        # NOTE: Limit AZs to avoid reaching resource quotas
        vpc = ec2.Vpc(self, "DashboardVPC", max_azs=2)

        cluster = ecs.Cluster(self, "DashboardCluster", vpc=vpc)

        repository = ecr.Repository(
            self, "DashboardRepository", repository_name="nccid-dashboard"
        )
        secret = secretsmanager.Secret(
            self, "DashboardSecret", secret_name="nccid-dashboard-secrets"
        )
        service_secret = ecs.Secret.from_secrets_manager(secret)

        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self,
            "DashboardService",
            cluster=cluster,
            task_image_options={
                "image": ecs.ContainerImage.from_ecr_repository(
                    repository=repository, tag=image_tag.value_as_string
                ),
                "secrets": [service_secret],
            },
            platform_version=ecs.FargatePlatformVersion.VERSION1_4,
        )

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP inbound from VPC",
        )

        core.CfnOutput(
            self,
            "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name,
        )

        cert = _acm.Certificate.from_certificate_arn(
            self, "cert", cert_arn.value_as_string
        )

        origin = _origins.HttpOrigin(
            domain_name=fargate_service.load_balancer.load_balancer_dns_name
        )
        behaviour = _cloudfront.BehaviorOptions(origin=origin)

        distribution = _cloudfront.Distribution(
            self,
            "nccid-dasboard-dist",
            default_behavior=behaviour,
            certificate=cert,
            domain_names=[domain_name.value_as_string],
        )
        # Explicit dependency setup
        distribution.node.add_dependency(fargate_service.load_balancer)

        # Outputs
        distribution_domain = core.CfnOutput(  # noqa:  F841
            self,
            "nccidDashboardDomain",
            value=distribution.distribution_domain_name,
            description="Cloudfront domain to set the CNAME for.",
        )
