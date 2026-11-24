"""Rename the patient column insurance_number to policy_number.

What: renames the database column, so the policy numbers stay in place
under the new field name.

Why pre-: this must happen before Odoo compares the table with the new
code. At that moment the old column still exists and the new one does
not yet. As a post- script it would be too late: Odoo would already have
created an empty policy_number column and, when it removes the obsolete
field insurance_number, dropped the old column together with its data.

Without it: every policy number is lost (checked: 0 of 7 values left).

Safe to run twice: nothing happens if the old column is already gone or
the new one already exists.
"""

from odoo.tools import sql

TABLE = "hr_hospital_patient"


def migrate(cr, version):
    """Rename the column if the database still has the old name."""
    if not version:
        return
    if sql.column_exists(cr, TABLE, "insurance_number") and not sql.column_exists(
        cr, TABLE, "policy_number"
    ):
        sql.rename_column(cr, TABLE, "insurance_number", "policy_number")
