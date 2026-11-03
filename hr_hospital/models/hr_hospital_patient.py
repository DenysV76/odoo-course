import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HrHospitalPatient(models.Model):
    _name = "hr.hospital.patient"
    _inherit = "hospital.medic.info"
    _description = "Patient"

    name = fields.Char()

    active = fields.Boolean(default=True)
    description = fields.Text()

    personal_doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Personal Doctor",
    )
    doctor_history_ids = fields.One2many(
        comodel_name="hospital.doctor.history",
        inverse_name="patient_id",
        string="Personal Doctor History",
    )
    insurance_number = fields.Char(
        string="Insurance Policy Number",
        size=20,
    )
    phone = fields.Char()
    visit_ids = fields.One2many(
        comodel_name="hr.hospital.visit",
        inverse_name="patient_id",
        string="Visits",
    )
    visit_count = fields.Integer(compute="_compute_visit_count")

    @api.depends("visit_ids")
    def _compute_visit_count(self):
        for patient in self:
            patient.visit_count = len(patient.visit_ids)

    def action_open_visits(self):
        """Open the visit history of this patient."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Visits",
            "res_model": "hr.hospital.visit",
            "view_mode": "list,form,calendar",
            "domain": [("patient_id", "=", self.id)],
            "context": {"default_patient_id": self.id},
        }

    def action_create_visit(self):
        """Open a new visit form in a dialog with this patient pre-filled."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "New Visit",
            "res_model": "hr.hospital.visit",
            "view_mode": "form",
            "target": "new",
            "context": {"default_patient_id": self.id},
        }
