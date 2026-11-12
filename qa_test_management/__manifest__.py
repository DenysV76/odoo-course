{
    "name": "QA Test Management",
    "summary": "Test cases, requirements and test runs linked to project tasks",
    "description": """
QA Test Management
==================
Test cases and requirements linked many-to-many, test runs for project tasks
with Pass / Fail lines moved Draft -> In Progress -> Done by buttons, a retest
wizard, a PDF run report and Tester / QA Lead access groups.
""",
    "author": "Denys Vialov",
    "website": "https://github.com/DenysV76/odoo-course",
    "category": "Services/Project",
    "license": "LGPL-3",
    "version": "19.0.1.0.0",
    "depends": [
        "project",
    ],
    "data": [
        "security/qa_security.xml",
        "security/ir.model.access.csv",
        "data/qa_sequence_data.xml",
        "views/qa_menu.xml",
        "views/qa_functional_area_views.xml",
        "views/qa_tag_views.xml",
        "views/qa_test_case_views.xml",
        "views/qa_requirement_views.xml",
        "wizard/qa_retest_wizard_views.xml",
        "views/qa_test_run_views.xml",
        "views/qa_test_run_line_views.xml",
        "views/project_task_views.xml",
        "views/res_users_views.xml",
        "report/qa_test_run_reports.xml",
        "report/qa_test_run_templates.xml",
    ],
    "demo": [
        "demo/qa_users_demo.xml",
        "demo/qa_reference_demo.xml",
        "demo/qa_library_demo.xml",
        "demo/qa_test_run_demo.xml",
    ],
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
