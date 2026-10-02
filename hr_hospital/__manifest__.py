{
    "name": "Hospital",
    "summary": "Hospital HR",
    "author": "Denys Vialov",
    "website": "https://github.com/DenysV76/odoo-course",
    "category": "Customizations",
    "license": "LGPL-3",
    "version": "19.0.1.0.0",
    "depends": [
        "base",
    ],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/hr_hospital_menu.xml",
        "views/hr_hospital_doctor_views.xml",
        "views/hr_hospital_patient_views.xml",
        "views/hr_hospital_disease_views.xml",
        "views/hr_hospital_visit_views.xml",
        "views/hospital_doctor_category_views.xml",
        "views/hospital_doctor_history_views.xml",
        "data/hr_hospital_disease_data.xml",
        "data/hospital_doctor_category_data.xml",
    ],
    "demo": [
        "demo/hr_hospital_doctor_demo.xml",
        "demo/hr_hospital_patient_demo.xml",
        "demo/hospital_doctor_history_demo.xml",
    ],
    "installable": True,
    "auto_install": False,
}
