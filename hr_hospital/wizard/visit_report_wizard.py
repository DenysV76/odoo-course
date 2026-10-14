import logging
from datetime import datetime, time, timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class VisitReportWizard(models.TransientModel):
    _name = "visit.report.wizard"
    _description = "Patient Visits Report"

    doctor_ids = fields.Many2many(
        comodel_name="hr.hospital.doctor",
        string="Doctors",
    )
    patient_ids = fields.Many2many(
        comodel_name="hr.hospital.patient",
        string="Patients",
    )
    date_from = fields.Date(string="Period Start")
    date_to = fields.Date(string="Period End")
    only_done = fields.Boolean(string="Only Done Visits")
    disease_id = fields.Many2one(
        comodel_name="hr.hospital.disease",
        string="Disease",
    )

    @api.model
    def default_get(self, fields_list):
        """Pre-fill doctors or patients the wizard was opened from."""
        res = super().default_get(fields_list)
        context = self.env.context
        active_ids = context.get("active_ids") or []
        if context.get("active_model") == "hr.hospital.doctor":
            res["doctor_ids"] = [(6, 0, active_ids)]
        elif context.get("active_model") == "hr.hospital.patient":
            res["patient_ids"] = [(6, 0, active_ids)]
        return res

    def _get_visit_domain(self):
        """Build the visit search domain from the filled wizard fields.

        Visits are filtered by planned_date (Datetime) while the period is
        given in Dates, so the end bound is "before the start of the next
        day": comparing a Datetime with a bare Date would cut off the whole
        last day of the period.
        """
        self.ensure_one()
        domain = []
        if self.doctor_ids:
            domain.append(("doctor_id", "in", self.doctor_ids.ids))
        if self.patient_ids:
            domain.append(("patient_id", "in", self.patient_ids.ids))
        if self.date_from:
            domain.append(
                ("planned_date", ">=", datetime.combine(self.date_from, time.min))
            )
        if self.date_to:
            next_day = self.date_to + timedelta(days=1)
            domain.append(("planned_date", "<", datetime.combine(next_day, time.min)))
        if self.only_done:
            domain.append(("state", "=", "done"))
        if self.disease_id:
            domain.append(("disease_id", "=", self.disease_id.id))
        return domain

    def action_show_report(self):
        """Open the list of visits matching the wizard criteria."""
        return {
            "type": "ir.actions.act_window",
            "name": "Visits Report",
            "res_model": "hr.hospital.visit",
            "view_mode": "list,form",
            "domain": self._get_visit_domain(),
            "target": "current",
        }
