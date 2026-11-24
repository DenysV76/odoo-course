=========
Changelog
=========

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
