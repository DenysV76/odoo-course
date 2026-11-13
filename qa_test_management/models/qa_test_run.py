from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class QaTestRun(models.Model):
    """A test run: one round of testing of the feature described in a task.

    The run is the business process of the module:
    draft -> in_progress -> done, with cancel / reset to draft on the side.
    The state moves only through buttons; every button checks where the run
    is now, so a jump like draft -> done is refused.
    """

    _name = "qa.test.run"
    _description = "Test Run"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        copy=False,
        default="New",
    )
    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task",
        required=True,
        ondelete="restrict",
        tracking=True,
    )
    project_id = fields.Many2one(related="task_id.project_id", store=True)
    tester_id = fields.Many2one(
        comodel_name="res.users",
        string="Tester",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )
    date_start = fields.Datetime(string="Started", readonly=True, copy=False)
    date_end = fields.Datetime(string="Finished", readonly=True, copy=False)
    note = fields.Text(string="Comments")
    line_ids = fields.One2many(
        comodel_name="qa.test.run.line",
        inverse_name="run_id",
        string="Lines",
        copy=True,
    )
    line_count = fields.Integer(string="Cases", compute="_compute_counts", store=True)
    pass_count = fields.Integer(string="Passed", compute="_compute_counts", store=True)
    fail_count = fields.Integer(string="Failed", compute="_compute_counts", store=True)
    todo_count = fields.Integer(
        string="Not Executed", compute="_compute_counts", store=True
    )
    pass_rate = fields.Float(
        string="Pass Rate (%)", compute="_compute_counts", store=True
    )
    verdict = fields.Selection(
        selection=[("pass", "Pass"), ("fail", "Fail")],
        compute="_compute_counts",
        store=True,
        help="Fail as soon as one line failed; Pass only when every line passed.",
    )
    estimate_minutes = fields.Float(
        string="Estimate (min)",
        compute="_compute_estimate_minutes",
        help="Sum of the estimates of the test cases in the run.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Give every new run a reference from the sequence."""
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("qa.test.run")
        return super().create(vals_list)

    @api.depends("line_ids.result")
    def _compute_counts(self):
        """Count results of the lines and derive the verdict of the run."""
        for run in self:
            results = run.line_ids.mapped("result")
            run.line_count = len(results)
            run.pass_count = results.count("pass")
            run.fail_count = results.count("fail")
            run.todo_count = results.count(False)
            run.pass_rate = (
                100.0 * run.pass_count / run.line_count if run.line_count else 0.0
            )
            if run.fail_count:
                run.verdict = "fail"
            elif run.line_count and not run.todo_count:
                run.verdict = "pass"
            else:
                run.verdict = False

    @api.depends("line_ids.case_id.estimate_minutes")
    def _compute_estimate_minutes(self):
        """Sum the case estimates to plan the time of the run."""
        for run in self:
            run.estimate_minutes = sum(run.line_ids.case_id.mapped("estimate_minutes"))

    @api.constrains("state", "line_ids")
    def _check_done_lines(self):
        """Invariant: a finished run has lines, and every line has a result.

        Checked here and not in the Done button, so that it also guards writes
        that bypass the button (import, RPC, another module).
        """
        for run in self:
            if run.state != "done":
                continue
            if not run.line_ids or run.line_ids.filtered(lambda ln: not ln.result):
                raise ValidationError(
                    self.env._(
                        "Run %(run)s cannot be done: every line needs a result.",
                        run=run.name,
                    )
                )

    def action_start(self):
        """Draft -> In Progress. A run without lines has nothing to execute."""
        for run in self:
            if run.state != "draft":
                raise UserError(self.env._("Only a draft run can be started."))
            if not run.line_ids:
                raise UserError(
                    self.env._("Add at least one test case before starting the run.")
                )
        self.write({"state": "in_progress", "date_start": fields.Datetime.now()})

    def action_done(self):
        """In Progress -> Done."""
        for run in self:
            if run.state != "in_progress":
                raise UserError(self.env._("Only a running run can be finished."))
        self.write({"state": "done", "date_end": fields.Datetime.now()})

    def action_cancel(self):
        """Draft or In Progress -> Cancelled. A finished run stays as it is."""
        for run in self:
            if run.state not in ("draft", "in_progress"):
                raise UserError(
                    self.env._("Only a draft or running run can be cancelled.")
                )
        self.write({"state": "cancel"})

    def action_reset_draft(self):
        """Cancelled -> Draft, to reuse a run cancelled by mistake."""
        for run in self:
            if run.state != "cancel":
                raise UserError(
                    self.env._("Only a cancelled run can be reset to draft.")
                )
        self.write({"state": "draft", "date_start": False, "date_end": False})
