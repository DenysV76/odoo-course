from odoo import api, fields, models


class ResUsers(models.Model):
    """Show the testing workload of a user: runs assigned to them."""

    _inherit = "res.users"

    qa_run_ids = fields.One2many(
        comodel_name="qa.test.run",
        inverse_name="tester_id",
        string="Assigned Test Runs",
        groups="qa_test_management.group_qa_user",
    )
    qa_open_run_count = fields.Integer(
        string="Open Test Runs",
        compute="_compute_qa_open_run_count",
        groups="qa_test_management.group_qa_user",
        help="Draft and in-progress runs where the user is the tester.",
    )

    @api.depends("qa_run_ids.state")
    def _compute_qa_open_run_count(self):
        """Count open runs per tester with one grouped query."""
        counts = dict(
            self.env["qa.test.run"]._read_group(
                domain=[
                    ("tester_id", "in", self.ids),
                    ("state", "in", ("draft", "in_progress")),
                ],
                groupby=["tester_id"],
                aggregates=["__count"],
            )
        )
        for user in self:
            user.qa_open_run_count = counts.get(user, 0)

    def action_open_qa_runs(self):
        """Smart button: open the open test runs of this user."""
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "qa_test_management.qa_test_run_action"
        )
        action["domain"] = [
            ("tester_id", "=", self.id),
            ("state", "in", ("draft", "in_progress")),
        ]
        action["context"] = {"default_tester_id": self.id}
        return action
