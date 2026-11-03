import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrHospitalVisit(models.Model):
    _name = "hr.hospital.visit"
    _inherit = ["mail.thread"]
    _description = "Visit"

    state = fields.Selection(
        selection=[
            ("planned", "Planned"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="planned",
        required=True,
        tracking=True,
    )
    planned_date = fields.Datetime(
        string="Planned Date",
        default=fields.Datetime.now,
    )
    visit_date = fields.Datetime(string="Actual Visit Date")

    name = fields.Char()

    active = fields.Boolean(default=True)
    description = fields.Text()

    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Doctor",
        tracking=True,
    )
    patient_id = fields.Many2one(
        comodel_name="hr.hospital.patient",
        string="Patient",
    )
    disease_id = fields.Many2one(
        comodel_name="hr.hospital.disease",
        string="Disease",
    )
    summary = fields.Html()
    disease_visit_count = fields.Integer(
        string="Visits with This Disease",
        compute="_compute_disease_visit_count",
    )

    @api.depends("patient_id.name", "name", "planned_date")
    def _compute_display_name(self):
        for visit in self:
            label = visit.patient_id.name or visit.name or "Новий візит"
            if visit.planned_date:
                label = f"{label} — {visit.planned_date:%d.%m.%Y}"
            visit.display_name = label

    @api.depends("disease_id")
    def _compute_disease_visit_count(self):
        """Count all visits sharing each visit's disease, in one grouped query."""
        counts = dict(
            self._read_group(
                [("disease_id", "in", self.disease_id.ids)],
                ["disease_id"],
                ["__count"],
            )
        )
        for visit in self:
            visit.disease_visit_count = counts.get(visit.disease_id, 0)

    def action_open_disease_visits(self):
        """Open all visits with the same disease as this one (stat button)."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.disease_id.display_name,
            "res_model": "hr.hospital.visit",
            "view_mode": "list,form",
            "domain": [("disease_id", "=", self.disease_id.id)],
        }

    @api.model
    def _cron_cancel_overdue_visits(self):
        """Cancel planned visits whose planned date has already passed.

        Used both by the server action and by the daily cron, so it searches
        by itself instead of relying on selected records.
        """
        overdue = self.search(
            [
                ("state", "=", "planned"),
                ("planned_date", "<", fields.Datetime.now()),
            ]
        )
        overdue.write({"state": "cancelled"})
        _logger.info("Cancelled %s overdue visits", len(overdue))
        return True

    def write(self, vals):
        for visit in self:
            if visit.state == "done" and (
                "planned_date" in vals or "visit_date" in vals or "doctor_id" in vals
            ):
                raise ValidationError("Не можна редагувати вже відбувшийся візит")
            if visit.state == "done" and "active" in vals and not vals["active"]:
                raise ValidationError("Не можна архівувати вже відбувшийся візит")
        return super().write(vals)

    def unlink(self):
        if self.env.context.get("_force_unlink"):
            return super().unlink()
        for visit in self:
            if visit.state == "done":
                raise ValidationError("Не можна видаляти вже відбувшийся візит")
        return super().unlink()
