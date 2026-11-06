import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HospitalDoctorCategory(models.Model):
    """Qualification of a doctor; the Internship flag marks intern categories."""

    _name = "hospital.doctor.category"
    _description = "Doctor Category"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    is_internship = fields.Boolean(string="Internship")
    doctor_ids = fields.One2many(
        comodel_name="hr.hospital.doctor",
        inverse_name="category_id",
        string="Doctors",
    )

    _name_uniq = models.Constraint(
        "unique (name)",
        "A doctor category with this name already exists.",
    )
