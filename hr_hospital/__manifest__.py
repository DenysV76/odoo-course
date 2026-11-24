{
    "name": "Hospital",
    "summary": "Doctors, patients and visits with role-based access",
    "description": """
Hospital
========
Doctors with mentors and interns, patients with personal doctors, visits,
a hierarchical disease classifier, a PDF doctor report and five access groups
from Patient to Administrator. Translated into Ukrainian.
""",
    "author": "Denys Vialov",
    "website": "https://github.com/DenysV76/odoo-course",
    "category": "Human Resources",
    "license": "LGPL-3",
    "version": "19.0.1.1.0",
    "depends": [
        "base",
        "mail",
    ],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        "security/hr_hospital_security.xml",
        "security/ir.model.access.csv",
        "views/hr_hospital_menu.xml",
        "views/hr_hospital_doctor_views.xml",
        "views/hr_hospital_patient_views.xml",
        "views/hr_hospital_disease_views.xml",
        "views/hr_hospital_visit_views.xml",
        "views/hospital_doctor_category_views.xml",
        "views/hospital_doctor_history_views.xml",
        "wizard/mass_reassign_doctor_wizard_views.xml",
        "wizard/visit_report_wizard_views.xml",
        "wizard/disease_report_wizard_views.xml",
        "report/hr_hospital_doctor_reports.xml",
        "report/hr_hospital_doctor_templates.xml",
        "data/hr_hospital_disease_data.xml",
        "data/hospital_doctor_category_data.xml",
        "data/hr_hospital_visit_cron_data.xml",
    ],
    "demo": [
        "demo/hr_hospital_disease_demo.xml",
        "demo/hr_hospital_doctor_demo.xml",
        "demo/hr_hospital_patient_demo.xml",
        "demo/hr_hospital_users_demo.xml",
        "demo/hospital_doctor_history_demo.xml",
        "demo/hr_hospital_visit_demo.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
