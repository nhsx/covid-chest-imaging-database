from setuptools import setup, find_namespace_packages


def readme():
    """Load long Readme from file
    """
    with open("README.md") as f:
        return f.read()


setup(
    name="warehouse",
    version="0.1.0",
    author="Gergely Imreh",
    author_email="gergely.imreh@faculty.ai",
    description="NCCID warehouse pipeline module",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/nhsx/covid-chest-imaging-database",
    packages=find_namespace_packages(include=["warehouse"]),
    classifiers=["Programming Language :: Python :: 3",],
    python_requires=">=3.6",
    scripts=["bin/warehouseloader", "bin/submittingcentres"],
    # entry_points={
    #     "console_scripts": [
    #         "warehouseloader=warehouse.warehouseloader:main",
    #         "submittingcentres=warehouse.submittingcentres:main",
    #     ],
    # },
)
