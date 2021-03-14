# Local-Crontab Serverless infrastructure
This is the CDK code to deploy the backend infrastructure used for the front-end(not exists yet) of the [Local-Crontab](https://github.com/Sonic0/local-crontab) python module.  

<p align="center">
  <img src="https://raw.githubusercontent.com/Sonic0/local-crontab-serverless-infrastructure/main/imgs/Local-Crontab-Infra.png" title="Local-Crontab-Infrastructure">
</p>

## Try Lambda via SAM
https://docs.aws.amazon.com/cdk/latest/guide/sam.html

1. Run your AWS CDK app and create a AWS CloudFormation template.
```bash
cdk synth --no-staging > template.yaml
```
2. Find the logical ID for your Lambda function in _template.yaml_. It will look like _MyFunction12345678_, where 12345678 represents an 8-character unique ID that the AWS CDK generates for all resources. 
```bash
sam local generate-event apigateway aws-proxy --body '{"cron":"0 10 * * *", "timezone":"America/Denver"}' --stage v1 --method POST --path utc-converter --resource None > apigateway-event-example.json
```
3. Run the function by executing.
```bash
sam local invoke awslambda<ID> --profile <profile> --region <region> --event apigateway-event-example.json --debug
```

## Todo
- Enable CORS --> [example1](https://github.com/aws-samples/aws-cdk-examples/blob/master/python/api-cors-lambda/app.py)


## Starting with CDK Python projects!

- [First step](https://docs.aws.amazon.com/cdk/latest/guide/work-with-cdk-python.html)
- [Second step](https://docs.aws.amazon.com/cdk/latest/guide/core_concepts.html)

###  Useful CDK commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
