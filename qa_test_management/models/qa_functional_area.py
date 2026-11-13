from odoo import api, fields, models
from odoo.exceptions import ValidationError


class QaFunctionalArea(models.Model):
    """Business area a test case or requirement belongs to.

    Areas follow features and workflows, not Odoo modules. The hierarchy is
    kept shallow on purpose: an area may have a parent, but the parent itself
    must be a top-level area (two levels at most).
    """

    _name = "qa.functional.area"
    _description = "Functional Area"
    _order = "parent_id, sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    parent_id = fields.Many2one(
        comodel_name="qa.functional.area",
        string="Parent Area",
        ondelete="restrict",
        domain=[("parent_id", "=", False)],
    )
    child_ids = fields.One2many(
        comodel_name="qa.functional.area",
        inverse_name="parent_id",
        string="Sub-areas",
    )
    description = fields.Text()
    active = fields.Boolean(default=True)

    @api.depends("name", "parent_id.name")
    def _compute_display_name(self):
        """Show sub-areas as "Parent / Child"."""
        for area in self:
            if area.parent_id:
                area.display_name = f"{area.parent_id.name} / {area.name}"
            else:
                area.display_name = area.name

    @api.constrains("parent_id")
    def _check_parent_depth(self):
        """Allow two levels only; this also rules out cycles."""
        for area in self:
            if area.parent_id and (area.parent_id.parent_id or area.child_ids):
                raise ValidationError(
                    self.env._("Functional areas can be nested two levels deep only.")
                )
