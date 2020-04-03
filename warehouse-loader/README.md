# Warehouse Loading

Pipeline for processing incoming images and patient data files in the data warehouse.

This pipeline takes care of appropriate preprocessing of the image data, create
the data warehouse file layout, and split the appropriate training and validation (holdout)
sets based on patient IDs.

## Running the code

Install the required dependencies:

```shell
pip install -r requirements.txt
```

Ensure that relevant AWS credentials are exported to the shell where the script is running.
Set the working S3 bucket name with the `BUCKET_NAME` environment variable

```shell
export BUCKET_NAME=my-warehouse-bucket
```

then run the script directly.

```shell
python warehouse-loader.py
```

The results of the pipeline will be shown in the terminal, for example:

```shell
$ python warehouse-loader.py 
 - extract_raw_folders in=1 out=1 [done] 
 - extract_raw_files_from_folder in=1 out=385 [done] 
 - process_file in=385 out=385 [done] 
 - data_copy in=385 out=385 [done] 
 ```

## Pipeline overview

![Data warehouse loader pipeline overview](warehouse-loader-pipeline.png)

To get this image, install the Python dependencies, [Graphviz](https://www.graphviz.org/), and run:

```shell
bonobo inspect --graph warehouse-loader.py | dot -o warehouse_loader.png -T png
```
