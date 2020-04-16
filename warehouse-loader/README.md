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
bonobo run warehouse-loader.py
```

The results of the pipeline will be shown in the terminal, for example:

```shell
$ bonobo run warehouse-loader.py --env WAREHOUSE_BUCKET=bucketname
- load_existing_files in=1 out=1 [done]
- extract_raw_folders in=1 out=2 [done]
- extract_raw_files_from_folder in=2 out=55954 [done]
- process_image in=55954 out=111782 err=2 [done]
- process_dicom_data in=111782 out=55891 [done]
- upload_extracted_dicom_data in=55891 out=55891 [done]
- process_patient_data in=55954 out=61 [done]
- data_copy in=111843 out=111843 [done]
 ```

## Pipeline overview

![Data warehouse loader pipeline overview](warehouse-loader-pipeline.png)

To get this image, install the Python dependencies, [Graphviz](https://www.graphviz.org/), and run:

```shell
bonobo inspect --graph warehouse-loader.py | dot -o warehouse-loader-pipeline.png -T png
```

## Warehouse structure

The warehouse training data is organised into subfolders based on image types, patient ID,
and date, as follows:

```shell
/training/ct/PATIENT_ID/DATE/IMAGE_UUID.dcm
/training/ct-metadata/PATIENT_ID/DATE/IMAGE_UUID.json
/training/mri/PATIENT_ID/DATE/IMAGE_UUID.dcm
/training/mri-metadata/PATIENT_ID/DATE/IMAGE_UUID.json
/training/x-ray/PATIENT_ID/DATE/IMAGE_UUID.dcm
/training/x-ray-metadata/PATIENT_ID/DATE/IMAGE_UUID.json
/training/data/PATIENT_ID/DATE/status.json
/training/data/PATIENT_ID/DATE/data.json
```

For any given `PATIENT_ID/DATE` combination there's either a `status.json` (for patients with
negative test results), or `data.json` (for positive test results), but not both.
