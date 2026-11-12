from odoo import fields, models


class QaTag(models.Model):
    """Free label for test cases (smoke, regression, access rights...)."""

    _name = "qa.tag"
    _description = "QA Tag"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()
    description = fields.Char()

    _name_unique = models.Constraint(
        "UNIQUE(name)",
        "A tag with this name already exists.",
    )
