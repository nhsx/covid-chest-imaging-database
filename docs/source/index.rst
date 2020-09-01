National COVID-19 Chest Image Database (NCCID)
==============================================

The National COVID-19 Chest Imaging Database (NCCID) comprises chest X-ray,
CT and MR images and other relevant information of patients with suspected
COVID-19. The database has been created to enable the development and validation
of automated analysis technologies that may prove effective in supporting COVID-19
care pathways, and to accelerate research projects to better understand the disease.


What data is collected
----------------------

The NCCID collects processed digital chest X-ray, CT and MR images as well as DICOM
header information (de-identified). Associated clinical data (de-identified) from
the collection sites is also gathered. Data will be collected for all COVID-19
positively-swabbed patients, and a smaller sample of COVID-19 negatively-swabbed
patients.

The categories of data collected are:

- Routine demographic data
- Routine cardiorespiratory assessment data at presentation
- All CXRs performed during evaluation for COVID-19
- All CT scans performed during evaluation for COVID-19
- All chest imaging performed in the 3 years preceding the first COVID-19-related
  imaging study (for COVID-19 positively-swabbed patients only)
- Scans (including MR) performed to investigate cardiac damage thought to be
  COVID-19-related
- Biochemical and haematological routinely collected data
- Outcome data, including time to mechanical ventilation, discharge and death

The full list of clinical data points collected for positive and negative
patients can found in the template spreadsheets on the
`Guidance And Documentation For Collection Sites <https://medphys.royalsurrey.nhs.uk/nccid/guidance.php>`_
page.


Data collection
---------------

If you have already joined the NCCID as a data collection site,
please visit `this website <https://medphys.royalsurrey.nhs.uk/nccid/index.php>`_.

If you would like to join the NCCID as a data collection site, please ask your
radiology department to contact imaging@nhsx.nhs.uk and we will send them the
relevant documentation.

The hospitals and trusts already contributing data to NCCID are listed below:

- `Royal United Hospitals Bath NHS Foundation Trust <https://www.ruh.nhs.uk/>`_
- `Brighton and Sussex University Hospitals NHS Trust <https://www.bsuh.nhs.uk/>`_
- `London North West University Healthcare NHS Trust <https://www.lnwh.nhs.uk/>`_
- `George Eliot Hospital NHS Trust <http://www.geh.nhs.uk/>`_
- `Cwm Taf Morgannwg University Health Board <https://cwmtafmorgannwg.wales/>`_
- `Hampshire Hospitals NHS Foundation Trust <https://www.hampshirehospitals.nhs.uk/>`_
- `Betsi Cadwaladr University Health Board <https://bcuhb.nhs.wales/>`_
- `Ashford and St Peter's Hospitals <http://www.ashfordstpeters.nhs.uk/>`_
- `Royal Cornwall Hospitals NHS Trust <https://www.royalcornwall.nhs.uk/>`_
- `Sheffield Children's NHS Foundation Trust <https://www.sheffieldchildrens.nhs.uk/>`_
- `Liverpool Heart and Chest Hospital NHS Foundation Trust <https://www.lhch.nhs.uk/>`_
- `Norfolk and Norwich University Hospitals NHS Foundation Trust <http://www.nnuh.nhs.uk/>`_
- `Royal Surrey NHS Foundation Trust <https://www.royalsurrey.nhs.uk/>`_
- `Sandwell and West Birmingham NHS Trust <https://www.swbh.nhs.uk/>`_
- `West Suffolk NHS Foundation Trust <https://www.wsh.nhs.uk/Home.aspx>`_
- `Somerset NHS Foundation Trust <https://www.somersetft.nhs.uk/>`_
- `Cambridge University Hospitals NHS Foundation Trust <https://www.cuh.nhs.uk/>`_
- `Imperial College Healthcare NHS Trust <https://www.imperial.nhs.uk/>`_

.. To add a site to the map below, please add an entry to
   source/scripts/hospital_locations.csv

.. _mapped-sites:

.. bokeh-plot:: scripts/maps.py
    :source-position: none

All participating hospitals and trusts will be cited in any publication
resulting from the use of NCCID data.


What the data can be used for
-----------------------------

This project aims to produce improvements in healthcare delivery for COVID-19
patients by creating a national resource for chest imaging research.

The research enabled by the chest imaging database will provide information
and tools that, in the context of the COVID-19 pandemic, support:

- The determination of disease severity
- Clinically useful diagnosis and prognosis
- Patient triage and management
- Decision making

We expect the data will be used to:

- Develop image processing software. *Example*: An AI model that determines
  COVID-19 risk score from chest X-rays.
- Mathematical Modelling. *Example*: A mathematical model that utilises chest
  X-rays to determine which patients in A&E will need a ventilator during
  their subsequent hospital stay.
- Validation of AI products. *Example*: A study to determine the extent to
  which an AI model for the diagnosis of COVID-19 trained on non-UK data
  retains its performance when applied on data from UK patients.
- Teaching resource for radiologists. *Example*: A teaching environment for
  radiologists where learners are presented with chest images, requested to
  diagnose COVID-19 cases, and receive feedback on their input.


How to request access to data
-----------------------------

Users (including software vendors, academics and clinicians) requiring access to
the database should fill in :download:`this form <docs/NCCID_Data_Access_Request_Form.docx>`
and provide a signed copy of the :download:`Data Access Framework Contract <docs/NCCID_Data_Access_Framework_Contract.docx>`
(if first time applying) and a :download:`Data Access Agreement <docs/NCCID_Data_Access_Agreement.docx>`.
All documents should be sent to NHSX by contacting imaging@nhsx.nhs.uk.

Please note that research groups affiliated with a hospital can only request access to NCCID data if their hospital is already a collection site.


How requests are assessed
-------------------------

Access requests will be assessed by a committee of experts including:

- **4 or more** scientific advisors
- **4 or more** technology advisors
- **2 or more** information-governance advisors
- **2 or more** patient/ethics advisors
- **2 or more** system advisors to evaluate the positive impact to the NHS overall
- An administrator to manage the access requests
- A chair person (this could be any of the advisors above)

Decisions will be guided by the following criteria:

- Relevance to COVID-19
- Scientific merit of the proposed work
- Technical feasibility
- Ability to deliver the work and track record of the applicants
- Reasonable evidence that access to the data can benefit patients and the NHS
- Compliance with GDPR and NHS standards of information governance
- IT security

Applications are subject to external peer review if deemed proportionate and
where the necessary expertise is not available within the committee.

Please note that data access is subject to a Data Access Agreement and a
Data Access Framework Contract between the applicant and NHSX, for teaching,
research and software development/validation purposes that address the COVID-19
pandemic.

Any access to the data and licences to use will expire when the COVID-19 COPI
(COVID-19 – Notice under Regulation 3(4) of the Health Service Control of Patient
Information Regulations 2002) ceases effect.


.. Table of contents below, put all front page text above this

.. toctree::
   :hidden:
   :caption: Technical documentation

   data_access

.. toctree::
   :hidden:
   :caption: Other Information

   NCCID_Collaborative
   project_summaries
   faq

