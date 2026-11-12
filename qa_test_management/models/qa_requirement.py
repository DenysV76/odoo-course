from odoo import api, fields, models

from .qa_test_case import PRIORITY_SELECTION


class QaRequirement(models.Model):
    """Atomic acceptance criterion that outlives the task it came from.

    Coverage is the link requirement <-> test case: a requirement without
    cases is not covered by tests.
    """

    _name = "qa.requirement"
    _description = "Requirement"
    _inherit = ["mail.thread"]
    _order = "priority desc, name"

    name = fields.Char(string="Title", required=True, tracking=True)
    description = fields.Text(help="One requirement - one acceptance criterion.")
    active = fields.Boolean(default=True)
    priority = fields.Selection(
        selection=PRIORITY_SELECTION,
        default="1",
        required=True,
        tracking=True,
    )
    area_id = fields.Many2one(
        comodel_name="qa.functional.area",
        string="Functional Area",
        required=True,
        ondelete="restrict",
    )
    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Source Task",
        help="Task (specification) where the requirement first appeared.",
    )
    author_id = fields.Many2one(
        comodel_name="res.users",
        string="Author",
        default=lambda self: self.env.user,
    )
    case_ids = fields.Many2many(
        comodel_name="qa.test.case",
        relation="qa_requirement_test_case_rel",
        column1="requirement_id",
        column2="case_id",
        string="Test Cases",
    )
    case_count = fields.Integer(compute="_compute_case_count", store=True)

    @api.depends("case_ids")
    def _compute_case_count(self):
        """Count linked test cases; zero means the requirement is not covered."""
        for requirement in self:
            requirement.case_count = len(requirement.case_ids)
