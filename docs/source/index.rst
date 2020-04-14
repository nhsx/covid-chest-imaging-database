.. Chest Data Warehouse documentation master file, created by
   sphinx-quickstart on Wed Apr  1 20:03:09 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

National COVID-19 Chest Image Database (NCCID)
==============================================

The National COVID-19 Chest Imaging Database (NCCID) comprises chest X-ray,
CT and MR images and other relevant information of patients with suspected
COVID-19. The database has been created to enable the development and
validation of automated analysis technologies that may prove effective in
supporting COVID-19 care pathways, and to accelerate research projects to
better understand the disease.


Information for accessing data
------------------------------


How to express your interest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We are working to set up processes and infrastructure for data access. We
will update this page as soon as these are finalised.

In the meantime, users (researchers, developers, clinicians...) who would
like to access the database can submit their “Expression of Interest” by
filling in :download:`this form <docs/NCCID_Expression_of_Interest_Form.docx>`,
and sending it to imaging@nhsx.nhs.uk. We will register all expressions
of interest, and send notifications as soon as data access becomes possible.

.. note::
   The Expression of Interest form is different from the
   Data Access Request form, which we will make available at a later stage.


Instructions for data collection sites
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have already joined the NCCID as a data collection site,
please visit `this website <https://medphys.royalsurrey.nhs.uk/nccid/index.php>`_.

If you would like to join the NCCID as a data collection site, please ask your
radiology department to contact imaging@nhsx.nhs.uk and we will send them
the relevant documentation.


What data is collected
----------------------

The NCCID collects processed digital chest X-ray, CT and MR images as well as
DICOM header information (de-identified). Associated clinical data (de-identified)
from the collection sites is also gathered. Data will be collected for all COVID-19
positively-swabbed patients, and a smaller sample of COVID-19 negatively-swabbed
patients.

The categories of data collected are:

- Routine demographic data
- Routine cardiorespiratory assessment data at presentation
- All CXRs performed during evaluation for COVID-19
- All CT scans performed during evaluation for COVID-19
- All chest imaging performed in the 3 years preceding the first COVID-19-related
  imaging study (for COVID-19 positively-swabbed patients only)
- Scans (including MR) performed to investigate cardiac damage thought to be COVID-19-related
- Biochemical and haematological routinely collected data
- Outcome data, including time to mechanical ventilation, discharge and death

The full list of clinical data points collected for positive and negative
patients can found in the documents below:

- `Covid-19 Data (Positive) Template v1.4 (Excel) <https://medphys.royalsurrey.nhs.uk/nccid/guidance/COVID-19_NCCID_covid_positive_data_template_v1_4.xlsx>`_
- `Covid-19 Status (Negative) Template v1.0 (Excel) <https://medphys.royalsurrey.nhs.uk/nccid/guidance/COVID-19_NCCID_covid_status_negative_data_template_v1_0.xlsx>`_


What the data can be used for
-----------------------------

This project aims to produce improvements in healthcare delivery for COVID-19
patients by creating a national resource for chest imaging research.

The research enabled by NCCID will provide information and tools that, in the
context of the COVID-19 pandemic, support:

- The determination of disease severity
- Clinically useful diagnosis and prognosis
- Patient triage and management
- Decision making

We expect the data will be used as follows:

- Image processing software. *Example*: An AI model that determines
  COVID-19 risk score from chest X-rays.
- Mathematical Modelling. *Example*: A mathematical model that utilises
  chest X-rays to determine which patients in A&E will need a ventilator
  during their subsequent hospital stay.
- Validation of AI products. *Example*: A study to determine the extent
  to which an AI model for the diagnosis of COVID-19 trained on non-UK
  data retains its performance when applied on data from UK patients.
- Teaching resource for radiologists. *Example*: A teaching environment for
  radiologists where learners are presented with chest images, requested
  to diagnose COVID-19 cases, and receive feedback on their input.
