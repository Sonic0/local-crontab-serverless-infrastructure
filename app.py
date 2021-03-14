#!/usr/bin/env python3
import os
from aws_cdk import core

from local_crontab_serverless_infrastructure.apigateway_stack import ApiGatewayStack
from local_crontab_serverless_infrastructure.lambda_stack import LambdaStack

app = core.App()

env_EU = core.Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
    region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]))

ApiGatewayStack(app, "ApiGLocalCronStack")  # provide Env in the case of Custom Domain
LambdaStack(app, "LambdaLocalCronStack")

app.synth()
