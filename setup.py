import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="local_crontab_serverless_infrastructure",
    version="0.0.1",

    license="MIT",

    description="Simple serverless infrastructure to expose a rest api for local-crontab python package",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Andrea Salvatori",

    package_dir={"": "local_crontab_serverless_infrastructure"},
    packages=setuptools.find_packages(where="local_crontab_serverless_infrastructure"),

    install_requires=[
        "aws-cdk.core",
        "aws-cdk.aws_lambda",
        "aws-cdk.aws_apigateway",
        "aws-cdk.aws_logs",
        "jinja2"
    ],

    python_requires=">=3.8",

    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
