"""Fill the new patient field first_visit_date from the visits.

What: sets first_visit_date to the date of the earliest visit that took
place (state "done", actual visit date set). Planned and cancelled visits
do not count. Patients without such visits keep an empty value.

Why post-: the column first_visit_date is created by Odoo when it syncs
the table with the new code, which happens after the pre- scripts. In a
pre- script the UPDATE fails with ``column "first_visit_date" of relation
"hr_hospital_patient" does not exist``. In post- the column is there and
the visits table is unchanged, so one UPDATE fills it.

Without it: the field stays empty for all existing patients; only data
entered after the update would be correct.

Safe to run twice: the UPDATE computes the same value again.

The date is taken from the UTC timestamp, the way it is stored.
"""


def migrate(cr, version):
    """Copy the earliest done visit date to every patient that has one."""
    if not version:
        return
    cr.execute(
        """
        UPDATE hr_hospital_patient p
           SET first_visit_date = v.first_date
          FROM (
                SELECT patient_id, min(visit_date)::date AS first_date
                  FROM hr_hospital_visit
                 WHERE state = 'done'
                   AND visit_date IS NOT NULL
                   AND patient_id IS NOT NULL
              GROUP BY patient_id
               ) v
         WHERE v.patient_id = p.id
        """
    )
