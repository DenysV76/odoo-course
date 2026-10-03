import logging

from odoo import fields, models

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
