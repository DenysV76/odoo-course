# ruff: noqa: F821  (env is provided by odoo-bin shell)
"""Own records for the upgrade test database (block 7, step 1).

Run once on a fresh database with hr_hospital 19.0.1.0.0 and demo data::

    python odoo/odoo-bin shell -c config/odoo.conf -d hospital_upgrade \
        < custom_addons/odoo-course/hr_hospital/doc/seed_before.py

Adds 5 patients and 6 visits. The policy numbers cover every case the
Char -> Integer step has to handle: plain digits, digits with spaces,
letters (AB-1234), a number too big for an integer, and no policy at all.
"""

Patient = env["hr.hospital.patient"]
Visit = env["hr.hospital.visit"]
doctor = env.ref("hr_hospital.hr_hospital_doctor_demo_1")

patients = Patient.create(
    [
        {"name": "Upgrade Test 1 (digits)", "insurance_number": "100200"},
        {"name": "Upgrade Test 2 (spaces)", "insurance_number": " 300 400 "},
        {"name": "Upgrade Test 3 (letters)", "insurance_number": "AB-1234"},
        {"name": "Upgrade Test 4 (too big)", "insurance_number": "98765432109"},
        {"name": "Upgrade Test 5 (no policy, no visits)"},
    ]
)
p1, p2, p3, p4, _p5 = patients

Visit.create(
    [
        # p1: two done visits, the earliest one is 2026-03-10.
        {
            "patient_id": p1.id,
            "doctor_id": doctor.id,
            "state": "done",
            "planned_date": "2026-05-20 09:00:00",
            "visit_date": "2026-05-20 09:30:00",
        },
        {
            "patient_id": p1.id,
            "doctor_id": doctor.id,
            "state": "done",
            "planned_date": "2026-03-10 09:00:00",
            "visit_date": "2026-03-10 10:00:00",
        },
        # p2: a done visit and an earlier cancelled one (must be ignored).
        {
            "patient_id": p2.id,
            "doctor_id": doctor.id,
            "state": "done",
            "planned_date": "2026-04-02 11:00:00",
            "visit_date": "2026-04-02 11:15:00",
        },
        {
            "patient_id": p2.id,
            "doctor_id": doctor.id,
            "state": "cancelled",
            "planned_date": "2026-01-15 11:00:00",
        },
        # p3: only a planned visit -> no first visit yet.
        {
            "patient_id": p3.id,
            "doctor_id": doctor.id,
            "state": "planned",
            "planned_date": "2026-12-01 12:00:00",
        },
        # p4: one done visit.
        {
            "patient_id": p4.id,
            "doctor_id": doctor.id,
            "state": "done",
            "planned_date": "2026-06-30 08:00:00",
            "visit_date": "2026-06-30 08:20:00",
        },
    ]
)
env.cr.commit()
print("patients:", Patient.search_count([]), "visits:", Visit.search_count([]))
