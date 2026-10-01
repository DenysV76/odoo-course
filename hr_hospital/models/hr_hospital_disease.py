import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HrHospitalDisease(models.Model):
    _name = "hr.hospital.disease"
    _description = "Disease"

    name = fields.Char()

    active = fields.Boolean(default=True)
    description = fields.Text()
