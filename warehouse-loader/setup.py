from setuptools import find_packages, setup


def readme():
    """Load long Readme from file"""
    with open("README.md") as f:
        return f.read()


setup(
    name="warehouse",
    version="0.1.0",
    author="Faculty",
    author_email="gergely.imreh@faculty.ai",
    description="NCCID warehouse pipeline module",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/nhsx/covid-chest-imaging-database",
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3"],
    python_requires=">=3.6",
    scripts=[
        "bin/warehouseloader",
        "bin/submittingcentres",
        "bin/dataprocess",
    ],
    install_requires=[
        # pipeline
        "bonobo==0.6.4",
        # s3
        "boto3==1.13.8",
        # image data
        "pydicom==1.4.2",
        # internal data management
        "pandas==1.1.5",
        "nccid_cleaning",
    ],
)
