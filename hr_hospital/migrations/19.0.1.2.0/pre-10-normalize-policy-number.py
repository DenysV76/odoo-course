"""Prepare policy_number for the change from Char to Integer.

What: keeps only the digits of every policy number. When the value had
anything besides digits and spaces (AB-1234), or does not fit into an
integer, the original text is copied into the new column policy_note,
and only then the number is cleaned or cleared. No value disappears
silently: whatever does not survive as a number survives as a note.

Why pre-: Odoo converts the column itself with
``ALTER COLUMN policy_number TYPE int4 USING policy_number::int4``. The
data must already be numeric by then, so the script runs while the column
is still varchar. As a post- script it would never run: the conversion
fails first and the whole update is rolled back.

Without it: the update fails with the PostgreSQL error ``invalid input
syntax for type integer: "UA-0002-2026"`` and the module stays on the old
version.

Safe to run twice: it does nothing once the column is no longer varchar,
and policy_note is created only if it is missing.
"""

from odoo.tools import sql

TABLE = "hr_hospital_patient"
INT_MAX = 2147483647


def migrate(cr, version):
    """Copy non-numeric policies to policy_note and keep only digits."""
    if not version:
        return
    columns = sql.table_columns(cr, TABLE)
    if columns.get("policy_number", {}).get("udt_name") not in ("varchar", "text"):
        return
    if "policy_note" not in columns:
        sql.create_column(cr, TABLE, "policy_note", "varchar", "Policy Note")

    # Keep the original text when it is more than digits and spaces.
    cr.execute(
        f"""
        UPDATE {TABLE}
           SET policy_note = policy_number
         WHERE policy_number IS NOT NULL
           AND policy_note IS NULL
           AND policy_number !~ '^[0-9 ]*$'
        """
    )
    # Digits only; empty strings become NULL.
    cr.execute(
        f"""
        UPDATE {TABLE}
           SET policy_number = NULLIF(regexp_replace(policy_number, '[^0-9]', '', 'g'), '')
         WHERE policy_number IS NOT NULL
        """
    )
    # Numbers that do not fit into int4 are kept only as a note.
    cr.execute(
        f"""
        UPDATE {TABLE}
           SET policy_note = COALESCE(policy_note, policy_number),
               policy_number = NULL
         WHERE length(ltrim(policy_number, '0')) > 10
            OR (length(ltrim(policy_number, '0')) = 10
                AND ltrim(policy_number, '0')::numeric > {INT_MAX})
        """
    )
