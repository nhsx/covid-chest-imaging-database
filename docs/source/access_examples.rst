
Accessing the NCCID data
========================

The data is stored in `Amazon Web Services S3 <https://aws.amazon.com/s3/>`_.
Once your organisation has been granted access, NHSX will send AWS credentials
by encrypted email. The credentials will allow accessing the data. 

We recommend accessing the data using the `Amazon Web Services Command Line Interface (AWS CLI) <https://aws.amazon.com/cli/>`_,
or client libraries that interact with S3. Some examples are provided below.

Warehouse structure
-------------------

The warehouse data is stored in the ``nccid-data-warehouse-prod`` S3 bucket, and access
is granted to different `prefixes <https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html#object-keys>`_.

The warehouse training data is organised into prefixes within the ``training`` prefix,
based on image types (or "modality"), patient ID, and date as follows:

.. code-block::

    # CT images & metadata
    training/ct/PATIENT_ID/STUDY_UID/SERIES_UID/IMAGE_UUID.dcm
    training/ct-metadata/PATIENT_ID/STUDY_UID/SERIES_UID/IMAGE_UUID.json

    # MRI images & metadata
    training/mri/PATIENT_ID/STUDY_UID/SERIES_UID/IMAGE_UUID.dcm
    training/mri-metadata/PATIENT_ID/STUDY_UID/SERIES_UID/IMAGE_UUID.json

    # X-ray images & metadata
    training/xray/PATIENT_ID/STUDY_UID/SERIES_UID/IMAGE_UUID.dcm
    training/xray-metadata/PATIENT_ID/STUDY_UID/SERIES_UID/IMAGE_UUID.json

    # Patient clinical data
    training/data/PATIENT_ID/status_DATE.json
    training/data/PATIENT_ID/data_DATE.json


* The ``ct``, ``mri``, ``xray`` folders hold the `DICOM <https://www.dicomstandard.org/>`_
  images of the given kind.
* The ``Patient_ID`` value is equivalent to the ``(0010,0020)`` DICOM `tag <https://www.dicomlibrary.com/dicom/dicom-tags/>`_
  from the images and ``Pseudonym`` field from the ``status_DATE.json`` and ``data_DATE.json``
  clinical data files.
* ``STUDY_UID`` and ``SERIES_UID`` are equivalent to the ``(0020,000D)`` and ``(0020,000E)``
  DICOM tags in the given images.
* The ``...-metadata`` folders hold the DICOM tags exported as JSON from the corresponding
  image file ``IMAGE_UUID.dcm`` into ``IMAGE_UUID.json`` to enable quick parsing without the
  need to download the given image
* The ``data`` folder holds the patient medical data, ``status_DATE.json`` files for negative
  results, and ``data_DATE.json`` file/files for positive results. ``DATE`` is formatted as
  ``YYYY-MM-DD``, for example ``2020-04-21``.

.. note::

    Over time there will be more images added to the warehouse, and they will show up as new
    patient folders, and new image folders with new images.


Using the AWS Command Line Interface
------------------------------------

The simplest way to retrieve the imaging data is using the AWS CLI:

.. code-block:: shell

    $ aws s3 sync s3://nccid-data-warehouse-prod/training/ct ct
    download: s3://nccid-data-warehouse-prod/training/ct/Covid1/1.2.3/A.B.C/x.y.z.dcm to ct/Covid1/1.2.3/A.B.C/x.y.z.dcm
    ...

Repeating this for all the relevant directories you would download the latest
data and images that you don't have locally:

.. code-block:: shell

    # Remove items from this array that you don't want to download
    modalities=("data" "ct" "ct-metadata" "mri" "mri-metadata" "xray" "xray-metadata")
    for modality in ${modalities[@]}; do
      aws s3 sync "s3://nccid-data-warehouse-prod/training/${modality}" "${modality}"
    done

In the above example `Bash arrays <https://www.gnu.org/software/bash/manual/html_node/Arrays.html>`_
were used (the ``modalities`` variable).

For more information check the `AWS CLI documentation <https://docs.aws.amazon.com/cli/index.html>`_.
If you encounter any problems, open an issue on our `GitHub repository <https://github.com/nhsx/covid-chest-imaging-database/issues>`_.

Using Python and Boto3
----------------------

If you are scripting access to files, we recommend using Python and `Boto3 <>`_

.. code-block:: python

    import boto3

    s3 = boto3.resource('s3')
    BUCKET_NAME = 'nccid-data-warehouse-prod'

    bucket = s3.Bucket(BUCKET_NAME)
    # List the objects at a given prefix
    print(list(bucket.objects.filter(Prefix='training/data')))

For more information check the `Boto3 documentation <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>`_.
If you encounter any problems, open an issue on our `GitHub repository <https://github.com/nhsx/covid-chest-imaging-database/issues>`_.
