=========
Changelog
=========

19.0.1.3.0 (2026-11-24)
-----------------------

* New field ``first_visit_date`` (Date) on patients.
* ``migrations/19.0.1.3.0/post-10-fill-first-visit-date.py`` fills it with
  the date of the earliest visit in state Done. Post-, because the column is
  created by Odoo only after the pre- scripts.

19.0.1.2.0 (2026-11-24)
-----------------------

* ``policy_number`` changes from Char to Integer; new field ``policy_note``
  (Char) keeps the original text of policies that were not plain numbers.
* ``migrations/19.0.1.2.0/pre-10-normalize-policy-number.py`` keeps only the
  digits, copies values with letters or too big for an integer into
  ``policy_note`` and clears those that do not fit. Pre-, because Odoo runs
  ``ALTER COLUMN ... TYPE int4`` right after and fails on text.

19.0.1.1.0 (2026-11-24)
-----------------------

* Patient field ``insurance_number`` renamed to ``policy_number``.
* ``migrations/19.0.1.1.0/pre-10-rename-policy-number.py`` renames the column.
  Pre-, because otherwise Odoo drops the old column with its data and
  creates a new empty one.

19.0.1.0.0 (2026-11-06)
-----------------------

Starting point of the upgrade scripts (block 7). Blocks 2-6 are released
under this one number, so the upgrade steps can use 1.1.0, 1.2.0 and 1.3.0.

* Five access groups (Patient, Intern, Doctor, Manager, Administrator) with
  per-group access lists and record rules.
* Demo users, one per group.
* ``System User`` field on patients.
* Ukrainian translation; translatable disease names.
* Tests for the doctor, visit and disease rules and for the access ladder.
* Module description, icon and banner.
* PDF report "Doctor Report" and doctor kanban improvements.
* Visit calendar, pivot and graph views; disease report wizard; daily
  cancellation of overdue visits.
* Doctors, patients, visits, diseases, doctor categories and personal doctor
  history; visit report and mass reassignment wizards.
