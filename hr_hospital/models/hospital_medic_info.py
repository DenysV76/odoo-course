import logging

from odoo import fields, models

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

    # TODO(2.1): метод _compute_age з @api.depends — вік у повних роках
    # від birth_date до сьогодні. Поки що заглушка, щоб модуль працював.
    def _compute_age(self):
        for record in self:
            record.age = 0
