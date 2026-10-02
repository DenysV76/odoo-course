import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HospitalDoctorCategory(models.Model):
    _name = "hospital.doctor.category"
    _description = "Doctor Category"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    doctor_ids = fields.One2many(
        comodel_name="hr.hospital.doctor",
        inverse_name="category_id",
        string="Doctors",
    )

    # TODO(1.2): унікальність назви через models.Constraint
