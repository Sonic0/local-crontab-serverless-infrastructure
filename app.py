#!/usr/bin/env python3

from aws_cdk import core

from local_crontab_serverless_infrastructure.apigateway_stack import ApiGatewayStack
from local_crontab_serverless_infrastructure.lambda_stack import LambdaStack

app = core.App()

ApiGatewayStack(app, "ApiGLocalCronStack")
LambdaStack(app, "LambdaLocalCronStack")

app.synth()
