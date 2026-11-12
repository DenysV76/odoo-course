from odoo import api, fields, models


class ProjectTask(models.Model):
    """Show the testing of a task right on the task: runs and requirements."""

    _inherit = "project.task"

    qa_run_ids = fields.One2many(
        comodel_name="qa.test.run",
        inverse_name="task_id",
        string="Test Runs",
        groups="qa_test_management.group_qa_user",
    )
    qa_requirement_ids = fields.One2many(
        comodel_name="qa.requirement",
        inverse_name="task_id",
        string="Requirements",
        groups="qa_test_management.group_qa_user",
    )
    qa_run_count = fields.Integer(
        string="Test Run Count",
        compute="_compute_qa_run_count",
        groups="qa_test_management.group_qa_user",
    )
    qa_verdict = fields.Selection(
        selection=[("pass", "Pass"), ("fail", "Fail")],
        string="Test Verdict",
        compute="_compute_qa_run_count",
        groups="qa_test_management.group_qa_user",
        help="Verdict of the latest finished test run of the task.",
    )

    @api.depends("qa_run_ids.state", "qa_run_ids.verdict")
    def _compute_qa_run_count(self):
        """Count runs and take the verdict of the latest finished one.

        One grouped query for all tasks instead of a search per task.
        """
        counts = dict(
            self.env["qa.test.run"]._read_group(
                domain=[("task_id", "in", self.ids)],
                groupby=["task_id"],
                aggregates=["__count"],
            )
        )
        for task in self:
            task.qa_run_count = counts.get(task, 0)
            done_runs = task.qa_run_ids.filtered(lambda run: run.state == "done")
            task.qa_verdict = done_runs.sorted("date_end")[-1:].verdict

    def action_open_qa_runs(self):
        """Smart button: open the test runs of this task."""
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "qa_test_management.qa_test_run_action"
        )
        action["domain"] = [("task_id", "=", self.id)]
        action["context"] = {"default_task_id": self.id}
        return action
