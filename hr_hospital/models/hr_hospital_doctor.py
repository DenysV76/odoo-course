import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HrHospitalDoctor(models.Model):
    _name = "hr.hospital.doctor"
    _description = "Doctor"

    name = fields.Char()

    active = fields.Boolean(default=True)
    description = fields.Text()

    observing_doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Observing Doctor",
    )
    category_id = fields.Many2one(
        comodel_name="hospital.doctor.category",
        string="Category",
    )
