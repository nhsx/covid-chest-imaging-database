# ALL_COLUMNS = [
#     "Pseudonym",
#     "SubmittingCentre",
#     "SwabStatus",
#     "OtherDataSources",
#     "ethnicity",
#     "sex_update",
#     "age_update",
#     "filename_covid_status",
#     "filename_earliest_date",
#     "filename_latest_date",
#     "swab_date",
#     "date_last_known_alive",
#     "date_of_1st_cxr",
#     "date_of_2nd_cxr",
#     "date_of_acquisition_of_1st_rt-pcr",
#     "date_of_acquisition_of_2nd_rt-pcr",
#     "date_of_admission",
#     "date_of_death",
#     "date_of_intubation",
#     "date_of_itu_admission",
#     "date_of_positive_covid_swab",
#     "date_of_result_of_1st_rt-pcr",
#     "date_of_result_of_2nd_rt-pcr",
#     "latest_swab_date",
#     "smoking_status",
#     "pack_year_history",
#     "pmh_hypertension",
#     "pmh_ckd",
#     "if_ckd_stage",
#     "pmh_cvs_disease",
#     "pmh_lung_disease",
#     "pmh_diabetes_mellitus_type_2",
#     "current_acei_use",
#     "current_angiotension_receptor_blocker_use",
#     "current_nsaid_used",
#     "duration_of_symptoms",
#     "respiratory_rate_on_admission",
#     "heart_rate_on_admission",
#     "fiO2_percentage",
#     "o2_saturation",
#     "pao2",
#     "systolic_bp",
#     "diastolic_bp",
#     "temperature_on_admission",
#     "news2_score_on_arrival",
#     "wcc_on_admission",
#     "lymphocyte_count_on_admission",
#     "platelet_count_on_admission",
#     "crp_on_admission",
#     "d-dimer_on_admission",
#     "fibrinogen__if_d-dimer_not_performed",
#     "ferritin",
#     "urea_on_admission",
#     "creatinine_on_admission",
#     "troponin_i",
#     "troponin_t",
#     "apache_score_on_itu_arrival",
#     "1st_rt-pcr_result",
#     "2nd_rt-pcr_result",
#     "cxr_severity",
#     "cxr_severity_3",
#     "covid_code",
#     "covid_code_2",
#     "final_covid_status",
#     "itu_admission",
#     "intubation",
#     "death",
# ]

PMH_COLUMNS = [
    "smoking_status",
    "pack_year_history",
    "pmh_hypertension",
    "pmh_ckd",
    "if_ckd_stage",
    "pmh_cvs_disease",
    "pmh_lung_disease",
    "pmh_diabetes_mellitus_type_2",
    "current_acei_use",
    "current_angiotension_receptor_blocker_use",
    "current_nsaid_used",
]

ADMISSION_COLUMNS = [
    "duration_of_symptoms",
    "respiratory_rate_on_admission",
    "heart_rate_on_admission",
    "fiO2_percentage",
    "o2_saturation",
    "pao2",
    "systolic_bp",
    "diastolic_bp",
    "temperature_on_admission",
    "news2_score_on_arrival",
    "wcc_on_admission",
    "lymphocyte_count_on_admission",
    "platelet_count_on_admission",
    "crp_on_admission",
    "d-dimer_on_admission",
    "fibrinogen__if_d-dimer_not_performed",
    "ferritin",
    "urea_on_admission",
    "creatinine_on_admission",
    "troponin_i",
    "troponin_t",
    "apache_score_on_itu_arrival",
]


OUTCOME_COLUMNS = [
    "1st_rt-pcr_result",
    "2nd_rt-pcr_result",
    "cxr_severity",
    "cxr_severity_3",
    "covid_code",
    "covid_code_2",
    "final_covid_status",
    "itu_admission",
    "intubation",
    "death",
]


DATE_COLUMNS = [
    "date_last_known_alive",
    "date_of_1st_cxr",
    "date_of_2nd_cxr",
    "date_of_acquisition_of_1st_rt-pcr",
    "date_of_acquisition_of_2nd_rt-pcr",
    "date_of_admission",
    "date_of_death",
    "date_of_intubation",
    "date_of_itu_admission",
    "date_of_positive_covid_swab",
    "date_of_result_of_1st_rt-pcr",
    "date_of_result_of_2nd_rt-pcr",
    "latest_swab_date",
]

DEMOGRAPHIC_COLUMNS = [
    "age_update",
    "sex_update",
    "ethnicity",
]

COLS_MAP = {
    "All": set(
        ADMISSION_COLUMNS
        + DATE_COLUMNS
        + DEMOGRAPHIC_COLUMNS
        + PMH_COLUMNS
        + OUTCOME_COLUMNS
    ),
    "Admission": set(ADMISSION_COLUMNS),
    "Date": set(DATE_COLUMNS),
    "Demographic": set(DEMOGRAPHIC_COLUMNS),
    "Medical History": set(PMH_COLUMNS),
    "COVID": set(OUTCOME_COLUMNS),
}


def in_column(field):
    field_column = None
    for key in COLS_MAP:
        if field in COLS_MAP[key]:
            field_column = key
            break
    return field_column
