.. _AI_Performance_Assessment:

Performance Assessment Call
===========================

Call for AI driven COVID-19 models: Performance assessment using the National COVID-19 Chest Imaging Database 
------------------------------------------------------------------------------------------------------------

Introduction
------------
| The `National COVID-19 Chest Imaging Database (NCCID) <https://nhsx.github.io/covid-chest-imaging-database/>`_ was created as part of the NHS AI Lab’s response to the coronavirus pandemic. The NCCID is currently the largest database of medical images from COVID patients in the UK, and a world-class initiative accelerating the development of AI technologies. This database will be an important resource to train and assess the performance of AI technologies that can be used as part of the ongoing response to COVID-19. The majority of scans collected by the NCCID are chest X-rays and come from people with and without  COVID-19. The database also holds some additional data about the patients who tested positive, such as their gender and age. A portion of these images and clinical data points has been set aside as ‘unseen’ for the purpose of assessing the performance and fairness of COVID-19 related AI models.

| The NHS AI Lab is now inviting research institutions and technology companies that have been developing AI models **using COVID-19 chest imaging data** to apply to have their model’s performance assessed on the NCCID’s unseen dataset. The assessment will be commissioned by NHSX to independent assessors, who will carry out the work with NHSX involvement and supervision. 


The importance of performance assessment on an unseen, representative dataset
-----------------------------------------------------------------------------
| The performance of AI models is linked to the characteristics of the data that they have been trained on, and those they encounter once put into clinical practice. This is the source of an important concern about the use of AI in healthcare: how to ensure that the claims made about a model will prove to be the case in the real world, where the data can be different from that used to develop it.

| Assessing the performance of AI models on a dataset that is representative of the UK population reduces the potential for bias and provides NHS commissioners and healthcare regulators with the evidence to judge the safety, efficacy, and generalisability of AI models before they are used in clinical practice. The NHS AI Lab has been working closely with NHS commissioners, regulators and end-users to define this process, and this performance assessment exercise will help to inform how this process may be carried out in the future.


How do I apply?
---------------
| Before applying, please ensure you are submitting an application for an AI technology developed using chest imaging data that addresses needs connected to COVID-19. 

| Applications from technology developers with products that have already achieved ISO13485 certification or other Quality Management System (QMS) certification are particularly welcome. **This is not a prerequisite for a product to be eligible for this assessment.** However, please note that it is a prerequisite of both the derogation and standard pathways for gaining the UKCA/CE mark.

| If you would like to apply, please complete this `application form <https://forms.gle/bcerY7XQcxeZj4Lg9/>`_ . If you have any questions, please contact us on imaging@nhsx.nhs.uk. **The application process is open from now and will close at 1pm on 28 May 2021.** This will be followed by a 3-week review process by a pool of expert reviewers, by the end of which you will receive feedback on the outcome of your application. 


What will I receive at the end of the assessment?
-------------------------------------------------
| The technology developer will receive a written report from the external assessors that documents how the AI model in question performed against the defined performance criteria. This will include an assessment of model performance (sensitivity, specificity etc.), and clinical applicability that can be used as evidence to support applications to the MHRA for derogation of UKCA/CE marking or via standard conformance assessment processes.

| In addition, depending on the outcome of the exercise, NHSX can support technology developers in identifying and making introductions to NHS trusts which have expressed an interest in commissioning new AI technologies.


Is this a route to regulatory conformance?
------------------------------------------
No, it is important to note that this process does not replace the path to achieve UKCA/CE/UKNI marking. This is considered to be a validation study and does not qualify as a clinical investigation for the purposes of clinical evaluation. In the context of bringing AI models to fruition as part of the COVID-19 response, the developers undergoing the proposed performance assessment process will, depending on the outcome of the exercise, be able to generate high quality evidence that their model performs as intended, which they can submit to the Medicines and Healthcare products Regulatory Agency (MHRA) to support their application for derogation (for more information please visit `Exemptions from Devices regulations during the coronavirus outbreak <https://www.gov.uk/guidance/exemptions-from-devices-regulations-during-the-coronavirus-covid-19-outbreak#exemptions-for-all-other-kind-of-medical-device/>`_ on the Gov.uk website). 

| Alternatively, standard routes to conformity under the device regulations remain open. Evidence generated via the proposed performance assessment process may form part of a standard regulatory submission. For more information please visit `How to comply with the legal requirements in Great Britain <https://www.gov.uk/guidance/medical-devices-how-to-comply-with-the-legal-requirements/>`_ on the Gov.uk website. 


What will this exercise involve for the technology developer?
-------------------------------------------------------------
| The NHS AI Lab will be using independent assessors to run the exercise, and assess the performance of the technology developer’s AI model. By doing this, NHSX aims to source deep subject matter expertise on both a technical and clinical level, in order to ensure that the exercise is carried out effectively and objectively. The validation will be performed within a cloud-computing infrastructure provided by NHSX, containing the NCCID unseen dataset. This will guarantee the dataset remains in a safe and secure location, and mitigate the risk of data being shared. The NHS AI Lab’s Programme Management Office will oversee the process.


How will the performance of an AI model be assessed?
----------------------------------------------------
| The assessment will be conducted on retrospective data and the following steps will take place:
- •The external assessors will prepare an analysis plan, including performance criteria, before the start of the assessment. To support this, NHSX will facilitate access to a network of regulators, subject matter experts and end users.
- •The technology developer will need to provide precise indications of use for their product. These will be the mechanism by which the performance criteria are tailored to the AI model, and the only input of the developer towards them.
- •Depending on the AI model to be assessed, it may be necessary for the assessors to source additional data externally and curate the resources. This is to ensure a dataset large and representative enough to perform an effective assessment. Note that pseudonymised data that does not contain patient identifiable information will be used throughout this process. 
Due to the continuous growth of the NCCID, the unseen dataset and any complementary data will be versioned appropriately to ensure a fair comparison between models, if required.


What infrastructure will be provided for the assessment process?
----------------------------------------------------------------
| The computational environment to run the exercise will be provided by NHSX via an AWS sub account on the existing NCCID infrastructure. The infrastructure will have the following:
- -Access to the NCCID unseen dataset will be in the form of an S3 bucket. The provision of this infrastructure by NHSX is to ensure the assessment is carried out within a secure environment that meets the requirements set by information governance. Please note that, at no time, will the technology developer have access to the NCCID unseen dataset.
- -Any additional infrastructure required to run the validation process will be hosted within this computational environment, but will be developed by the external assessors. This may include infrastructure that enables the following:
- •Deployment of the AI software by the technology developer, such that the technology developer can then be locked out whilst the external assessment is performed.
- •Additional security measures to ensure that both the data and the AI software are protected. 
- •Assessment of the AI Product against defined performance metrics. 
| Note that the deployment of the AI software for assessment will be achieved through coordination between the external assessors and the technology developer. We anticipate the AI model may be run on a virtual machine, and therefore may need to be containerised using technologies such as Docker.


How will the technology developer’s intellectual property be protected?
-----------------------------------------------------------------------
| As part of the assessment process:

- •All members of the performance assessment exercise team, including the external assessors, will be bound to confidentiality by contractual arrangements. Where needed, additional Non-Disclosure Agreements (NDAs) will be put in place.
- •The computing infrastructure, on which the AI model is deployed, will ensure that the relevant access controls are in place to protect the Intellectual Property (IP) of the technology developer.
- •Under no circumstances will NHSX or its agents make claims to developer IP, and this will be captured in the contractual arrangements prior to commencing the exercise.


How long will the assessment process take?
------------------------------------------
| The process end-to-end will take approximately 12-16 weeks to complete, depending on the complexity of the model deployment and analysis.
How many AI models do you intend to assess?
This will depend on the number of applications received and the strength of the proposals. 


How much will this assessment cost me?
--------------------------------------
| NHSX will bear the cost of the performance assessment exercise.


How will applications be assessed?
----------------------------------
| Applications will be scored against a set of defined criteria for each of the following categories:

- •NHS importance
- •Technical feasibility
- •Financial viability

| Further details for the above criteria are included in the Application Form. 

| Applications will be assessed by expert peer reviewers and an appointed committee consisting of technical and clinical advisors.

