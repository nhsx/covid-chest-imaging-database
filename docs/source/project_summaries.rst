.. _project_summaries:

NCCID project summaries
=======================

The core of the NCCID initiative is to provide value to the public in response to the COVID-19 crisis.
For this reason, NCCID wishes to share information on how the data is being utilised by approved institutions and researcherts, to inform the wider community of patients, staff and interested public.

Below is a list of the projects currently ongoing.


University College London
-------------------------

University College London plans to store the NCCID data in a highly secure XNAT repository to enable imaging-based research at UCL Centre for Medical Image Computing (CMIC). In particular, researchers at CMIC will use these data to build artificial intelligence models to automatically detect COVID-19 patients based on their CT or X-ray images, such that, in the future, these images can be screened automatically before doctors read them. This will significantly save time in managing future outbreaks. The research also involves building computational models to analyse the outcomes for those with confirmed COVID-19 diagnosis, predicting best management for individual patients. These predictions may shorten their hospital stay, reduce complications and even save lives. Finally, the project will investigates methods to deploy these developed models to local hospitals quickly and safely.  

University of Cambridge
-------------------------
It is strongly believed that early detection of COVID-19 and intervention leads to lower Covid-19 mortality because it enables disease treatment via
oxygen therapy and control of spread via isolation. The diagnosis of COVID-19 must be confirmed by reverse-transcription
polymerase chain reaction (RT-PCR) or gene sequencing for respiratory or blood specimens. However, testing the general population is proving to be
very challenging because of various reasons including limitations of sample collection and transportation, kit performance and availability,
limitations in capacity, etc.
 
Chest scans could include x-rays, CT and MRI scans. Chest CT scans are used to examine lung tissues and often used for further investigation after
an abnormal chest x-ray. Chest MRI scans provide a detailed picture of the chest wall, heart, and blood vessels. These scans are carried out routinely
for a variety of medical reasons, including preparation for surgery, annual follow-ups, accident and emergency, etc. The creation of computer systems that can automatically process these scans to detect and identify signs of Covid-19 can provide added value for the NHS with no significant additional burden on staff, resources, operational costs, etc. The development of these systems require the implementation of cutting-edge image processing and artificial intelligence technologies.
 
X-ray images and CT scans can also be useful in monitoring the progression of Covid-19 patients as they can reveal if their lungs are filled with sticky mucus that can lead to breathing problems and provide a benchmark for comparisons with previous scans.
 
This project aims to find the visual signatures of Covid-19, as they appear in chest scans, that can lead to accurate diagnostic and prognosis for use in
hospital settings. Automated imaging algorithms, aided by advanced artificial intelligence techniques, can detect some of the abnormal features
appearing in these scans, such as ground glass patterned areas, Ground glass, Crazy paving, Vascular dilatation, Traction Bronchiectasis. These features are generally not specific to Covid-19 and could be seen with other infections. Hence, it is important to develop AI techniques to aid the imaging analysis to increase the accuracy of diagnostic.

University of Bradford
-------------------------
Coronavirus Disease 2019 (COVID-19) is highly contagious, and severe cases can lead to pneumonia and ultimately death. The diagnosis can be confirmed by laboratory testing; however, the test has low sensitivity which leads to late diagnosis and treatment. Chest X-rays and CT scans provide valuable diagnostic and monitoring information that can complement the laboratory and clinical data. In this project, we propose to develop an open-source artificial intelligence tool that combines chest imaging data and clinical data to support the diagnosis, triaging and prognosis for COVID-19 in the UK. This will make clinical decisions more efficient, accurate, timely, and potentially cheaper, leading to better patient outcomes. 

V7
-------------------------
V7 Labs https://v7labs.com is predicting the severity and likelihood of ICU admission of patients via chest x-rays using a deep image retrieval method. By collaborating with NHSx, the San Matteo hospital of Pavia, and multiple international collaborators, they have assembled over 9,000 comparable patient cases, of which over 2,000 are confirmed to have COVID-19. Among these V7’s model has learned to assess the patient’s severity, and whether the patient is at risk of entering the ICU solely based on a single chest x-ray and their patient profile. The AI model currently predicts whether a patient will enter the ICU with 85% accuracy when a first x-ray is taken, based on a validation set of 200 unseen cases from Italy, the UK, and US of varying ethnicities and ages.
 
V7’s approach involved the extraction of the lungs from a patient’s x-ray to avoid any potential forms of bias. By analysing only the status of pixels inside the lungs, V7’s AI is not able to deduct (and therefore “cheat”) whether a patient is supine, elderly, or had their x-ray taken with a portable scanner. This approach solely observes the patient’s normalised lungs, alongside any quantitative readings taken at the hospital.
 
The image retrieval component of the AI also presents the 5 most-similar cases to the patient, enabling a deeper level of explainability than simple regions of interest (ROI) on the image. This allows clinician to observe the patient pathway taken by other highly correlated cases.
By solely relying on one x-ray, the AI model is able to predict ICU admission with an 85% accuracy rate. The team is now adding additional data to this baseline score to push results to an even higher level and detect potential edge cases. 

Aidence
-------------------------
Chest CT scans are used in hospitals across the globe to image the severity of COVID-19 lung involvement and guide the appropriate patient management. Artificial intelligence (AI) designed for radiologists can increase the speed of reporting on these scans and support timely patient
triaging.

Aidence has set-up an international consortium, ICOVAI, to create an AI solution for COVID-19 on chest CTs. The consortium is a collaboration between clinical centers, hospitals, AI companies, and distribution partners.

ICOVAI’s AI solution will automatically detect COVID-19 on chest CTs and assess the extent of lung tissue affected. Its quantitative analysis can be used to guide hospital management, such as bed capacity on wards, or predicting the need for ICU care.

The consortium aims to reduce the workload and pressure that the medical staff are facing during the pandemic. The software will be particularly useful when test kits are absent or inconclusive, and when radiologists are unavailable or lack specific COVID-19 training.

To train a well-performing model, ICOVAI is using high-quality datasets from diverse CT scanners, hospitals, and countries. The patient data is anonymised and processed in line with the GDPR. The product will comply with the Medical Device Regulation (MDR), 2017/745, to ensure clinical safety and quality.

The AI solution will be made available not-for-profit for the NHS and European hospitals. The project is backed by the EU.
