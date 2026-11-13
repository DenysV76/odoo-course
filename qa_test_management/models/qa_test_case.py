from odoo import api, fields, models

PRIORITY_SELECTION = [
    ("0", "Low"),
    ("1", "Medium"),
    ("2", "High"),
    ("3", "Critical"),
]


class QaTestCase(models.Model):
    """One atomic check: preconditions, steps and the expected result.

    A test case knows nothing about tasks. It is linked to a task only through
    test run lines, so the same case is reused across many runs.
    """

    _name = "qa.test.case"
    _description = "Test Case"
    _inherit = ["mail.thread"]
    _order = "priority desc, name"

    name = fields.Char(required=True, tracking=True)
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
        tracking=True,
    )
    tag_ids = fields.Many2many(comodel_name="qa.tag", string="Tags")
    preconditions = fields.Text()
    steps = fields.Text(required=True)
    expected_result = fields.Text(required=True)
    estimate_minutes = fields.Float(
        string="Estimate (min)",
        help="Expected time to execute the case once, in minutes.",
    )
    automation_status = fields.Selection(
        selection=[
            ("manual", "Manual"),
            ("candidate", "Automation Candidate"),
            ("automated", "Automated"),
            ("never", "Not Automatable"),
        ],
        default="manual",
        required=True,
    )
    requirement_ids = fields.Many2many(
        comodel_name="qa.requirement",
        relation="qa_requirement_test_case_rel",
        column1="case_id",
        column2="requirement_id",
        string="Requirements",
    )
    author_id = fields.Many2one(
        comodel_name="res.users",
        string="Author",
        default=lambda self: self.env.user,
    )
    run_line_ids = fields.One2many(
        comodel_name="qa.test.run.line",
        inverse_name="case_id",
        string="Run History",
    )
    run_count = fields.Integer(
        string="Executions",
        compute="_compute_run_stats",
        help="How many times the case got a result in a run.",
    )
    last_result = fields.Selection(
        selection=[("pass", "Pass"), ("fail", "Fail")],
        compute="_compute_run_stats",
    )
    last_run_date = fields.Datetime(
        string="Last Executed", compute="_compute_run_stats"
    )

    @api.depends("run_line_ids.result", "run_line_ids.executed_on")
    def _compute_run_stats(self):
        """Execution history: how often the case ran and how it ended last time."""
        for case in self:
            executed = case.run_line_ids.filtered("result").sorted("executed_on")
            last = executed[-1:]
            case.run_count = len(executed)
            case.last_result = last.result
            case.last_run_date = last.executed_on
