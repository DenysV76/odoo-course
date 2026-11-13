from odoo import Command, api, fields, models
from odoo.exceptions import UserError


class QaRetestWizard(models.TransientModel):
    """Create a retest run from the failed lines of a finished run.

    After a bug fix only the failed cases need to run again, so the new run
    gets exactly those cases instead of the whole original scope.
    """

    _name = "qa.retest.wizard"
    _description = "Retest Failed Cases"

    run_id = fields.Many2one(
        comodel_name="qa.test.run",
        string="Original Run",
        required=True,
        readonly=True,
    )
    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Task",
        required=True,
        help="Usually the same task, or the bug task where the fix was made.",
    )
    tester_id = fields.Many2one(
        comodel_name="res.users",
        string="Tester",
        required=True,
    )
    case_ids = fields.Many2many(
        comodel_name="qa.test.case",
        string="Cases to Retest",
        help="Failed cases of the original run. Remove the ones you skip.",
    )

    @api.model
    def default_get(self, fields_list):
        """Fill the wizard from the run it was opened on."""
        values = super().default_get(fields_list)
        run = self.env["qa.test.run"].browse(self.env.context.get("active_id"))
        if run.exists():
            failed = run.line_ids.filtered(lambda line: line.result == "fail")
            values.update(
                run_id=run.id,
                task_id=run.task_id.id,
                tester_id=run.tester_id.id,
                case_ids=[Command.set(failed.case_id.ids)],
            )
        return values

    def action_create_run(self):
        """Create the draft retest run and open it."""
        self.ensure_one()
        if self.run_id.state != "done":
            raise UserError(self.env._("Only a finished run can be retested."))
        if not self.case_ids:
            raise UserError(self.env._("Select at least one case to retest."))
        new_run = self.env["qa.test.run"].create(
            {
                "task_id": self.task_id.id,
                "tester_id": self.tester_id.id,
                "note": self.env._("Retest of %(run)s.", run=self.run_id.name),
                "line_ids": [
                    Command.create({"case_id": case.id}) for case in self.case_ids
                ],
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "qa.test.run",
            "res_id": new_run.id,
            "view_mode": "form",
            "target": "current",
        }
