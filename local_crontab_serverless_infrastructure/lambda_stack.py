from aws_cdk import (
    core,
    aws_lambda as lambda_,
    aws_iam as iam
)
from aws_cdk.core import Tags

class LambdaStack(core.Stack):
    def __init__(self, app: core.App, id: str, **kwargs):
        super().__init__(app, id, **kwargs)

        aws_lambda_name = self.node.try_get_context("awsLambdaName")
        aws_lambda_exec_role = self.node.try_get_context("awsLambdaExecRole")

        # Create role for the lambda Edge function
        aws_lambda_role = iam.Role(
            self, "AwsLambdaLocalCrontabRole",
            role_name=aws_lambda_exec_role,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ],
            description="Policy assumed by Lambda for Local-crontab service")

        aws_lambda_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["*"],
            actions=[
                "logs:CreateLogStream",
                "logs:CreateLogGroup",
                "logs:PutLogEvents"]
            )
        )

        # install lambda requirements inside a container
        aws_lambda_code = lambda_.Code.from_asset(
            path=f'lambda/',
            bundling=core.BundlingOptions(
                image=core.BundlingDockerImage.from_registry('python:3.8-slim'),
                command=[
                    'bash', '-c', ' && '.join([
                        'cp -r /asset-input/* /asset-output/',
                        'rm -rf /asset-output/__pycache__ /asset-output/tests',
                        'pip3 install --upgrade -r requirements.txt -t /asset-output',
                        'ls -lart /asset-output'
                    ])
                  ],
                user='root'
            )
        )

        aws_lambda = lambda_.Function(
            self, "AwsLambda",
            function_name=aws_lambda_name,
            code=aws_lambda_code,
            handler=f"{aws_lambda_name}.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            role=aws_lambda_role,
            description="Lambda Edge to authorize access to api documentations"
            )

        aws_lambda_event_invoke_cnf = lambda_.EventInvokeConfig(
            self, "AwsLambdaInvokeCnf",
            function=aws_lambda,
            max_event_age=core.Duration.seconds(60),
            retry_attempts=1
        )

        Tags.of(aws_lambda).add("Scope", "local-crontab")

        # Output of resources

        # Lambda
        self._function = aws_lambda

        core.CfnOutput(
            self, "LambdaName",
            description="Lambda Function Name",
            value=aws_lambda.function_name,
        )

        core.CfnOutput(
            self, "LambdaArn",
            description="Lambda Function Arn",
            value=aws_lambda.function_arn,
        )


    # Using the property decorator
    @property
    def main_func(self) -> lambda_.IFunction:
        return self._function

