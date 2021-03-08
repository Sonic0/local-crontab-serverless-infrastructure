from aws_cdk import (
    aws_apigateway as apigw,
    aws_logs as logs,
    core
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
        aws_lambda_exec_role = self.node.try_get_context("awsLambdaExecRole")

        # Load a template from file
        template = env.get_template(openapi3_template_spec_file)
        rendered_text = template.render(
            logo_link=self.node.try_get_context("ApiDocLogo"),
            aws_lambda_name=aws_lambda_name,
            aws_lambda_exec_role=aws_lambda_exec_role)
        # save the rendered results
        with open(rendered_openapi3_spec, "w") as file:
            file.write(rendered_text)


        # Create CloudWatch LogGroup destination
        aws_cloudwatch_api_loggroup = logs.LogGroup(
            self, "LocalCrontabApiCloudWatchLog",
            log_group_name=f'{aws_api_name}_logs',
            removal_policy=core.RemovalPolicy.RETAIN,
            retention=logs.RetentionDays.ONE_WEEK)

        # Create an API from OpenApi3 specification
        api_definition = apigw.AssetApiDefinition.from_asset(rendered_openapi3_spec)

        # Default Rest API stage
        api_stage = apigw.StageOptions(
            stage_name=api_version,
            logging_level=apigw.MethodLoggingLevel.INFO,
            # access_log_destination=apigw.AccessLogDestinationConfig(destination_arn=aws_cloudwatch_api_loggroup.log_group_arn),
            throttling_rate_limit=5,
            throttling_burst_limit=1,
            description="Default Stage"
            )

        aws_rest_api = apigw.SpecRestApi(
            self, "LocalCrontabApi",
            api_definition=api_definition,
            rest_api_name=aws_api_name,
            endpoint_types=[apigw.EndpointType.REGIONAL],
            retain_deployments=True,
            deploy_options=api_stage)

        Tags.of(aws_rest_api).add("Scope", "local-crontab")
