from aws_cdk import (
    core,
    aws_apigateway as apigw,
    aws_logs as logs,
    aws_iam as iam
)
from aws_cdk.core import Tags
from jinja2 import Environment, FileSystemLoader, select_autoescape


# Create a Jinja2 env to load OpenApi3 based on provided ENV
templateLoader = FileSystemLoader(searchpath="./")
env = Environment(
    loader=templateLoader,
    autoescape=select_autoescape(['yaml'])
)
openapi3_template_spec_file = './openapi_specification/local_crontab_api.yaml'
rendered_openapi3_spec = './openapi_specification/local_crontab_api_rendered.yaml'


class ApiGatewayStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        aws_api_name = self.node.try_get_context("apiName")
        api_version = self.node.try_get_context("ApiVersion")
        aws_default_region = self.node.try_get_context("awsDefaultRegion")
        aws_lambda_name = self.node.try_get_context("awsLambdaName")

        # Create role with Invoke permission
        aws_api_role = iam.Role(
            self, "AwsAPIGILambdaInvokeRole",
            role_name=self.node.try_get_context("awsApiGatewayInvokeRole"),
            assumed_by=iam.ServicePrincipal('apigateway.amazonaws.com'),
            description="Policy assumed by API Gateway to execute the target Lambda")

        aws_api_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=["*"],
                actions=["lambda:InvokeFunction"]
            )
        )

        # Load a template from file
        template = env.get_template(openapi3_template_spec_file)
        rendered_text = template.render(
            logo_link=self.node.try_get_context("ApiDocLogo"),
            aws_lambda_name=aws_lambda_name,
            aws_api_role=self.node.try_get_context("awsApiGatewayInvokeRole"))
        # save the rendered results
        with open(rendered_openapi3_spec, "w") as file:
            file.write(rendered_text)


        # Api gateway CloudWatch LogGroup destination
        aws_cloudwatch_api_loggroup = logs.LogGroup(
            self, "LocalCrontabApiCloudWatchLog",
            log_group_name=f'{aws_api_name}_logs',
            removal_policy=core.RemovalPolicy.RETAIN,
            retention=logs.RetentionDays.ONE_WEEK
        )

        # aws_api_stage_access_log_conf = apigw.AccessLogDestinationConfig(destination_arn=aws_cloudwatch_api_loggroup.log_group_arn)

        # Create an API from OpenApi3 specification
        api_definition = apigw.AssetApiDefinition.from_asset(rendered_openapi3_spec)

        # Default Rest API stage
        aws_api_stage = apigw.StageOptions(
            stage_name=api_version,
            data_trace_enabled=True,
            logging_level=apigw.MethodLoggingLevel.INFO,
            # access_log_destination=apigw.IAccessLogDestination(self),
            throttling_rate_limit=2,
            throttling_burst_limit=1,
            description="Default Stage"
        )

        aws_rest_api = apigw.SpecRestApi(
            self, "LocalCrontabApi",
            api_definition=api_definition,
            rest_api_name=aws_api_name,
            endpoint_types=[apigw.EndpointType.REGIONAL],
            retain_deployments=True,
            deploy_options=aws_api_stage
        )

        # ==== ================================================#
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/ApiKey.html
        aws_rest_api_key = apigw.ApiKey(
            self, "LocalCrontabApiKey",
            api_key_name="local-crontab-api-key",
            description="local-crontab service API Key",
            enabled=True,
            resources=[aws_rest_api]
        )

        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/UsagePlan.html
        #Rate:
        # 2 requests per second Burst
        # 1 requests Quota
        # 100 requests per day
        aws_rest_api_usage_plan = apigw.UsagePlan(
            self, "LocalCrontabUsagePlan",
            api_key=aws_rest_api_key,
            api_stages=[apigw.UsagePlanPerApiStage(
                api=aws_rest_api,
                stage=aws_rest_api.deployment_stage,
                # throttle=None # List of ThrottlingPerMethod. Not usefull in my case
            )],
            name="local-crontab-usage-plan",
            description="local-crontab usage plan",
            quota=apigw.QuotaSettings(
                limit=100,
                offset=0,
                period=apigw.Period.DAY
            ),
            throttle=apigw.ThrottleSettings(
                rate_limit=5,
                burst_limit=1
            )
        )

        # ====================================================#
        # ==== Code Example to create a CustomDomain Name ====#
        # ====
        # In my case I don't want to migrate this API from regional to EDGE, because of -->
        #   For an API Gateway Regional custom domain name, you must request or import the certificate in the same Region as your API.
        # ====================================================#

        # aws_domain_cert = cert_manage.Certificate.from_certificate_arn(
        #     self, "AwsRootDomainWilcardCert",
        #     certificate_arn=self.node.try_get_context("awsDomainCertArn")
        # )

        # aws_rest_api_domain = apigw.DomainName(
        #     self, "LocalCrontabApiDomain",
        #     mapping=aws_rest_api,
        #     domain_name=self.node.try_get_context("awsRoute53DomainName"),
        #     endpoint_type=apigw.EndpointType.REGIONAL,
        #     certificate=aws_domain_cert
        # )

        # aws_root_domain_zone = route53.HostedZone.from_lookup(
        #     self, "AwsRoute53ExistingZone",
        #     domain_name=self.node.try_get_context("awsRoute53DomainName"),
        #     private_zone=False)
        #
        # route53.ARecord(
        #     zone=aws_root_domain_zone,
        #     record_name=self.node.try_get_context("awsRoute53SubDomainName"),
        #     target=route53.RecordTarget(
        #         alias_target=route53.AliasRecordTargetConfig(
        #             dns_name=aws_rest_api_domain.domain_name,
        #             hosted_zone_id=aws_root_domain_zone.hosted_zone_id
        #         )
        #     ),
        #     comment="DNS record for Local-Crontab API"
        # )

        # =====================================================#

        Tags.of(aws_rest_api).add("Scope", "local-crontab")

        core.CfnOutput(
            self, "ApiGatewayName",
            description="Api Gateway name",
            value=aws_rest_api.rest_api_name,
        )
