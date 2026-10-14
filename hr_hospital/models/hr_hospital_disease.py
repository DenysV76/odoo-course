import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrHospitalDisease(models.Model):
    _name = "hr.hospital.disease"
    _description = "Disease"
    _order = "complete_name"

    name = fields.Char()

    active = fields.Boolean(default=True)
    description = fields.Text()

    parent_id = fields.Many2one(
        comodel_name="hr.hospital.disease",
        string="Parent Disease",
        index=True,
        ondelete="restrict",
    )
    child_ids = fields.One2many(
        comodel_name="hr.hospital.disease",
        inverse_name="parent_id",
        string="Sub-diseases",
    )

    complete_name = fields.Char(
        string="Full Path",
        compute="_compute_complete_name",
        recursive=True,
        store=True,
    )

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for disease in self:
            if disease.parent_id:
                disease.complete_name = (
                    f"{disease.parent_id.complete_name} / {disease.name}"
                )
            else:
                disease.complete_name = disease.name

    @api.depends("complete_name")
    def _compute_display_name(self):
        for disease in self:
            disease.display_name = disease.complete_name

    @api.constrains("parent_id")
    def _check_is_cycle(self):
        if self._has_cycle():
            raise ValidationError("Хвороба не може бути батьківською сама собі")
