import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HrHospitalVisit(models.Model):
    _name = "hr.hospital.visit"
    _description = "Visit"

    visit_date = fields.Datetime(
        string="Visit Date",
        default=fields.Datetime.now,
    )

    name = fields.Char()

    active = fields.Boolean(default=True)
    description = fields.Text()

    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Doctor",
    )
    patient_id = fields.Many2one(
        comodel_name="hr.hospital.patient",
        string="Patient",
    )
    disease_id = fields.Many2one(
        comodel_name="hr.hospital.disease",
        string="Disease",
    )
