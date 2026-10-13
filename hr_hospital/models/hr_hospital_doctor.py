import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

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

    @api.depends("category_id.is_internship")
    def _compute_is_intern(self):
        """Обрав спосіб - галочка на кваліфікації. Так здається надійніше ніж діставати кваліфікацію за ярлик,
        бо якщо хтось видалить картку, то код впаде. Плюс, якщо буде створено ще одну інтернську кваліфікацію
        (Інтерн-хірург), то вона інтерном не вважатиметься.
        """
        for doctor in self:
            doctor.is_intern = doctor.category_id.is_internship

    @api.constrains("mentor_id")
    def _check_is_intern(self):
        for doctor in self:
            if doctor.mentor_id.is_intern:
                raise ValidationError("Інтерн не може бути Ментором")

