from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class QaTestRunLine(models.Model):
    """One test case inside one run: the place where the result lives.

    The result is binary (Pass / Fail); an empty result means the line has not
    been executed yet.
    """

    _name = "qa.test.run.line"
    _description = "Test Run Line"
    _order = "run_id desc, sequence, id"
    _rec_name = "case_id"

    run_id = fields.Many2one(
        comodel_name="qa.test.run",
        string="Run",
        required=True,
        ondelete="cascade",
        index=True,
    )
    sequence = fields.Integer(default=10)
    case_id = fields.Many2one(
        comodel_name="qa.test.case",
        string="Test Case",
        required=True,
        ondelete="restrict",
    )
    result = fields.Selection(selection=[("pass", "Pass"), ("fail", "Fail")])
    comment = fields.Text(help="Reason for Fail, or what was special about a Pass.")
    executed_on = fields.Datetime(readonly=True, copy=False)
    executed_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Executed By",
        readonly=True,
        copy=False,
    )
    # Stored related fields: the pivot and graph group lines by them.
    state = fields.Selection(related="run_id.state", string="Run State")
    task_id = fields.Many2one(related="run_id.task_id", store=True)
    tester_id = fields.Many2one(related="run_id.tester_id", store=True)
    area_id = fields.Many2one(related="case_id.area_id", store=True)
    priority = fields.Selection(related="case_id.priority", store=True)

    _case_unique_per_run = models.Constraint(
        "UNIQUE(run_id, case_id)",
        "A test case can appear only once in a run.",
    )

    @api.constrains("result", "comment")
    def _check_fail_comment(self):
        """A failed line must say why it failed."""
        for line in self:
            if line.result == "fail" and not (line.comment or "").strip():
                raise ValidationError(
                    self.env._(
                        "Explain why case %(case)s failed in the comment.",
                        case=line.case_id.name,
                    )
                )

    @api.constrains("result")
    def _check_run_in_progress(self):
        """Results are entered only while the run is in progress."""
        for line in self:
            if line.result and line.run_id.state != "in_progress":
                raise ValidationError(
                    self.env._("Results can be set only in a run that is in progress.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        """Refuse new lines in a finished or cancelled run."""
        lines = super().create(vals_list)
        lines._check_run_editable()
        return lines

    def write(self, vals):
        """Lock lines of finished runs and stamp who executed a line and when."""
        self._check_run_editable()
        if "result" in vals:
            vals = dict(
                vals,
                executed_on=fields.Datetime.now() if vals["result"] else False,
                executed_by_id=self.env.uid if vals["result"] else False,
            )
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_closed_run(self):
        """Lines of a finished run are history and cannot be deleted."""
        self._check_run_editable()

    def _check_run_editable(self):
        """Raise if any line belongs to a done or cancelled run."""
        if self.run_id.filtered(lambda run: run.state in ("done", "cancel")):
            raise UserError(
                self.env._("Lines of a done or cancelled run cannot be changed.")
            )

    def action_set_pass(self):
        """Quick button in the run form: mark the line as passed."""
        self.write({"result": "pass"})

    def action_set_fail(self):
        """Quick button in the run form: mark the line as failed.

        The comment is checked by the constraint, so write it first.
        """
        self.write({"result": "fail"})
