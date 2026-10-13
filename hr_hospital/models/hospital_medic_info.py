import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HospitalMedicInfo(models.AbstractModel):
    _name = "hospital.medic.info"
    _description = "Medical Info (abstract)"

    blood_type = fields.Selection(
        selection=[
            ("o_pos", "O(I) Rh+"),
            ("o_neg", "O(I) Rh-"),
            ("a_pos", "A(II) Rh+"),
            ("a_neg", "A(II) Rh-"),
            ("b_pos", "B(III) Rh+"),
            ("b_neg", "B(III) Rh-"),
            ("ab_pos", "AB(IV) Rh+"),
            ("ab_neg", "AB(IV) Rh-"),
        ],
        string="Blood Type",
    )
    gender = fields.Selection(
        selection=[
            ("male", "Male"),
            ("female", "Female"),
        ],
    )
    birth_date = fields.Date()
    age = fields.Integer(compute="_compute_age")

    @api.depends("birth_date")
    def _compute_age(self):
        for record in self:
            if not record.birth_date:
                record.age = 0
                continue
            if (
                fields.Date.today().month < record.birth_date.month
                or fields.Date.today().month == record.birth_date.month
                and fields.Date.today().day < record.birth_date.day
            ):
                record.age = fields.Date.today().year - record.birth_date.year - 1
            else:
                record.age = fields.Date.today().year - record.birth_date.year
