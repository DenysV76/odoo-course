import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrHospitalDisease(models.Model):
    """Hierarchical disease classifier; names are translatable."""

    _name = "hr.hospital.disease"
    _description = "Disease"
    _order = "complete_name"

    name = fields.Char(required=True, translate=True)

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
        """Build the full path of the disease, e.g. "Infectious / Viral"."""
        for disease in self:
            if disease.parent_id:
                disease.complete_name = (
                    f"{disease.parent_id.complete_name} / {disease.name}"
                )
            else:
                disease.complete_name = disease.name

    @api.depends("complete_name")
    @api.depends_context("lang")
    def _compute_display_name(self):
        """Display a disease by its full path in the user's language.

        complete_name is stored, so it keeps only the source (English) names
        and is used for ordering; the path shown to users is built from the
        translated names of the disease and its parents.
        """
        for disease in self:
            names = []
            current = disease
            while current:
                names.append(current.name or "")
                current = current.parent_id
            disease.display_name = " / ".join(reversed(names))

    @api.constrains("parent_id")
    def _check_is_cycle(self):
        """Forbid a disease to become its own parent or ancestor."""
        if self._has_cycle():
            raise ValidationError(self.env._("A disease cannot be its own parent."))
