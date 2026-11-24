#!/bin/bash
# Control values of an hr_hospital upgrade test database.
# Usage: PGPASSWORD=... doc/check_upgrade.sh <db>   (user: $PGUSER, default odoo)
DB=${1:-hospital_upgrade}
export PGUSER=${PGUSER:-odoo} PGHOST=${PGHOST:-localhost}
q() { psql -d "$DB" -Atc "$1"; }
cols=$(q "select string_agg(column_name, ',' order by column_name)
            from information_schema.columns
           where table_name = 'hr_hospital_patient'
             and column_name in ('insurance_number', 'policy_number',
                                 'policy_note', 'first_visit_date')")
echo "version: $(q "select latest_version from ir_module_module where name = 'hr_hospital'")"
echo "patients: $(q 'select count(*) from hr_hospital_patient')  visits: $(q 'select count(*) from hr_hospital_visit')"
echo "patient columns: $cols"
for c in ${cols//,/ }; do
  echo "  $c filled: $(q "select count(*) from hr_hospital_patient where $c is not null")"
done
psql -d "$DB" -c "select id, name, $cols from hr_hospital_patient order by id"
