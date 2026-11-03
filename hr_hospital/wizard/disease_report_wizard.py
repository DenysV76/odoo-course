from datetime import datetime, time, timedelta

from odoo import api, fields, models


class DiseaseReportWizard(models.TransientModel):
    _name = "disease.report.wizard"
    _description = "Disease Report"

    doctor_ids = fields.Many2many(
        comodel_name="hr.hospital.doctor",
        string="Doctors",
    )
    disease_ids = fields.Many2many(
        comodel_name="hr.hospital.disease",
        string="Diseases",
    )
    date_from = fields.Date(string="Period Start")
    date_to = fields.Date(string="Period End")

    @api.model
    def default_get(self, fields_list):
        """Pre-fill the doctors the wizard was opened from."""
        res = super().default_get(fields_list)
        context = self.env.context
        if context.get("active_model") == "hr.hospital.doctor":
            res["doctor_ids"] = [fields.Command.set(context.get("active_ids") or [])]
        return res

    def _get_visit_domain(self):
        """Build the visit domain; an empty field means no restriction.

        The period is given in Dates while visits are filtered by the
        planned_date Datetime, so the end bound is "before the start of the
        next day" - otherwise the whole last day would be lost.
        """
        self.ensure_one()
        domain = []
        if self.doctor_ids:
            domain.append(("doctor_id", "in", self.doctor_ids.ids))
        if self.disease_ids:
            domain.append(("disease_id", "in", self.disease_ids.ids))
        if self.date_from:
            domain.append(
                ("planned_date", ">=", datetime.combine(self.date_from, time.min))
            )
        if self.date_to:
            next_day = self.date_to + timedelta(days=1)
            domain.append(("planned_date", "<", datetime.combine(next_day, time.min)))
        return domain

    def action_show_report(self):
        """Open the matching visits grouped by disease."""
        return {
            "type": "ir.actions.act_window",
            "name": "Disease Report",
            "res_model": "hr.hospital.visit",
            "view_mode": "list,form",
            "domain": self._get_visit_domain(),
            "context": {"search_default_group_by_disease": 1},
            "target": "current",
        }
