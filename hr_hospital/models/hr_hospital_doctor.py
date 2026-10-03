import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HrHospitalDoctor(models.Model):
    _name = "hr.hospital.doctor"
    _inherit = "hospital.medic.info"
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
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="System User",
    )
    is_intern = fields.Boolean(
        string="Is Intern",
        compute="_compute_is_intern",
        store=True,
    )
    mentor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Mentor",
    )

    # TODO(3.4 + 6): справжня логіка is_intern і docstring з обґрунтуванням
    # (розділ 6 завдання). Поки що заглушка: ніхто не інтерн.
    @api.depends("category_id")
    def _compute_is_intern(self):
        for doctor in self:
            doctor.is_intern = False

    # TODO(3.4): @api.constrains — не можна зберегти, якщо ментор сам інтерн
