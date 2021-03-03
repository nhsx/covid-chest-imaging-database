.. _faq:

************************
Resources for data users
************************


Data cleaning pipeline and guidelines
#####################################

We have created a `data cleaning pipeline <https://github.com/nhsx/nccid-cleaning>`_ in the form
of a Python library, which can be used to clean the accompanying clinical data to the images.
This will help with:

* Correcting format errors
* Removing anomalous data
* Remapping categorical values to standardised categories
* Extracting values embedded within strings
* Merging data under old or mis-typed column headers into the new/correct fields
* Standardising the scales of some clinical variables

In addition, we have created guidelines for interpreting the clinical data, compiled in
:download:`this spreadsheet <docs/NCCID_schema_compliance_v2.1.xlsx>`.
This will help with:

* Understanding what the expected data format is for each field
* Highlighting where there are known erroneous entries for each field
* Recommending remedial actions for erroneous entries within each field

An :download:`additional spreadsheet <docs/NCCID_site_specific_units.xlsx>` contains
information on submitting sites that use measurement units for various clinical variable fields
that is different from the overview of the above schema description. This will help with:

* Transforming clinical measurements on the same range

Please note that this sheet contains only a subset of potential submitting centres, and a
subset of clinical variables. Furthermore, responses for these submitting centres may
only represent a subset of their hospital sites, where units might vary from hospital to
hospital. The information presented here should only serve as a guide, and always be
checked against values to ensure they are sensible. For some fields you might have
to make decisions on data cleaning and potentially drop values that you think are
outside the plausible range or entered incorrectly.


Frequently Asked Questions
##########################

This is a list of Frequently Asked Questions with regards to the NCCID dataset content and usage.  Feel free to
suggest new entries!

.. contents:: Questions:
    :local:
    :backlinks: none


How often is new data uploaded to the database?
-----------------------------------------------

It varies but we are aiming for a new data release every week.


What is the "Final COVID Status" determined by? We're seeing patients with two negative PCRs with a positive final COVID status.
--------------------------------------------------------------------------------------------------------------------------------

The Final COVID Status is the final status that is available for each patient.
The fact that there are patients with multiple negative swab results and the final
status which is positive is an example of what happens sometimes in practice:
patients might get tested several times producing negative results, and then finally
result positive. This might be because sometimes tests are not accurate or because
patients fell ill between the initial and the final test.


Is COVID CODE = Normal the equivalent of "regular" Covid-19 or is it non-Covid-19?
----------------------------------------------------------------------------------

``COVID CODE = Normal`` refers to the cases where the X-Rays do not show signs of Covid-19,
this might be because the patient does not have it or because the patient has only very
mild symptoms.


What are the CXR severity scores?
---------------------------------
The severity scores associated with the chest X-Ray studies are subjective descriptions
provided by the radiologist reviewing the images, on a scale of three severity levels
(Mild = 1, Moderate = 2, Severe = 3).


Is the CXR severity score only available for the first two X-Ray studies?
-------------------------------------------------------------------------

Yes,the severity information is only available for the first two X-Ray studies
for each patient.


How can I match the clinical data points to the corresponding imaging scan?
---------------------------------------------------------------------------

The temporal information should help you match the information in the sheet
with the relevant imaging study: ``Date of 1st CXR`` and ``Date of 2nd CXR``
are the dates in which the first two X-Ray scans were taken and correspond to the
two severity values, the time information in the X-Ray's DICOM should then allow
you to identify the imaging scans that match with those dates.


Date format seems to be inconsistent across date variables (some are in US format and some are in UK format). Why is this? Is there a pattern?
----------------------------------------------------------------------------------------------------------------------------------------------

Yes, it is true that the date format is not consistent across all variables, but it
should be consistent within each single variable (i.e. if it is UK format, all entries
for that variable are in UK format).

The dates of the Date of acquisition of 1st RT-PCR and Date of acquisition of 2n RT-PCR are in
US format, however we have seen there are a few instances where some sites have inputted
additional text in these fields which will require a small amount of cleaning
(e.g. ``Date of 1st CXR`` with value ``[TEXT] - 2020-03-27``).

All other dates should be in UK or ISO format.


Have any of the dates been changed systematically as part of the anonymisation process? Or are the dates in the DICOM files and the clinical variables the actual dates of scans and tests?
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Most dates in the DICOM files have been offset. The excludes the Acquisition date
(if present) and the Study Date, so these can be used to identify the time of scan.
In addition, the patient's DOB has been reset to the year of birth followed by 0101.
The dates in the clinical data have not been touched.


There are cases where patients have multiple JSON files. Why is this? Which one is the correct one?
---------------------------------------------------------------------------------------------------

Situations with patients who have multiple JSON files can occur when the sites that
contribute data to NCCID have uploaded data, then revised/corrected and then
re-uploaded it. We are not currently over-writing files, as it would make data management
harder. We suggest that for each patient you utilise the latest JSON file that you have available.

Finally, there can also be cases in which the same patient went to two different hospitals,
and for which images have been received from two centres separately. In similar situations,
the older JSON files should be considered.


How can I combine the clinical data into a single table/dataset, selecting only the most recent "data" and/or "data" files for each patient?
--------------------------------------------------------------------------------------------------------------------------------------------

The development team prepared a tool to help you to aggregate JSON metadata and convert the results to CSV files. Please
check `this repository <https://bitbucket.org/scicomcore/nccid-data-to-csv/>`_, where the README contains all the relevant
information and the relevant download links.


How do I tell if the clinical data files are for positive and negative patients?
--------------------------------------------------------------------------------

There are two files, with ``status`` and ``data`` in the filename, that can be used to
differentiate between Covid-19 positive and negative patients. Negative patients
only have a ``status`` file, this is because data providers were told to only submit
the minimum information for the control cohort, to make it easier for them. Positives
can be identified by the presence of a ``data`` file which contains relevant clinical
information, such as their medical history. Some positive patients will have both files,
but their status file can be ignored.
