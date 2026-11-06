========
Hospital
========

Training module of the Odoo 19 developer course: doctors, patients and their
visits, with an access ladder of five groups and a Ukrainian translation.

Features
--------

* Doctors with categories, mentors and interns; kanban grouped by category.
* Patients with a personal doctor and the history of its changes.
* Visits with the states Planned / Done / Cancelled; calendar, pivot and
  graph views; done visits cannot be edited, archived or deleted.
* Hierarchical disease classifier; disease names are translatable.
* PDF report "Doctor Report" with the visit history and patients of a doctor.
* Wizards: visit report, disease report, mass reassignment of the personal
  doctor.
* Daily scheduled action that cancels overdue planned visits.

Access rights
-------------

Five groups in the *Hospital* section of user settings. Each group implies the
previous one: Patient, Intern, Doctor, Manager, Administrator.

* **Patient** reads own visits and own patient card.
* **Intern** reads and edits own visits.
* **Doctor** reads and edits own visits and visits of own interns.
* **Manager** reads and edits all visits and master data, cannot delete.
* **Administrator** can also delete any data of the module.

Internal users outside these groups have no access to the module data.

Installation
------------

#. Add the repository folder to ``addons_path``.
#. Install the module *Hospital* from the Apps menu.
#. Give users one of the *Hospital* groups in Settings > Users.

Demo data contain one user per group (login ``hospital_patient``,
``hospital_intern``, ``hospital_doctor``, ``hospital_manager``,
``hospital_admin``; the password equals the login).

Tests
-----

11 tests in ``tests/test_hr_hospital.py``::

    odoo-bin -d <db> -u hr_hospital --test-enable --stop-after-init

Credits
-------

Author: Denys Vialov.
