import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="nccid-dashboard",
    version="0.0.1",

    description="The NCCID dashboard",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "dashboard"},
    packages=setuptools.find_packages(where="dashboard"),

    install_requires=[
        "aws-cdk.core==1.82.0",
        "aws-cdk.aws-certificatemanager==1.82.0",
        "aws-cdk.aws-cloudfront==1.82.0",
        "aws-cdk.aws-cloudfront-origins==1.82.0",
        "aws-cdk.aws-ec2==1.82.0",
        "aws-cdk.aws-ecs==1.82.0",
        "aws-cdk.aws-ecs-patterns==1.82.0",
        "aws-cdk.aws-ecr==1.82.0",
        "aws-cdk.aws-secretsmanager==1.82.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
