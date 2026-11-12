from psycopg2 import IntegrityError

from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, new_test_user, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestQaTestManagement(TransactionCase):
    """Own logic of every model of the module, plus access rules."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tester = new_test_user(
            cls.env,
            login="test_qa_tester",
            groups="qa_test_management.group_qa_user,project.group_project_user",
        )
        cls.other_tester = new_test_user(
            cls.env,
            login="test_qa_tester_2",
            groups="qa_test_management.group_qa_user,project.group_project_user",
        )
        cls.lead = new_test_user(
            cls.env,
            login="test_qa_lead",
            groups="qa_test_management.group_qa_admin,project.group_project_user",
        )
        cls.area = cls.env["qa.functional.area"].create({"name": "Test Area"})
        cls.cases = cls.env["qa.test.case"].create(
            [
                {
                    "name": f"Test case {i}",
                    "area_id": cls.area.id,
                    "steps": "Do it",
                    "expected_result": "It works",
                    "estimate_minutes": 5 * (i + 1),
                }
                for i in range(3)
            ]
        )
        project = cls.env["project.project"].create({"name": "QA Project"})
        cls.task = cls.env["project.task"].create(
            {"name": "QA Task", "project_id": project.id}
        )

    def _create_run(self, tester=None, cases=None):
        """Draft run with one line per case."""
        return self.env["qa.test.run"].create(
            {
                "task_id": self.task.id,
                "tester_id": (tester or self.tester).id,
                "line_ids": [
                    Command.create({"case_id": case.id})
                    for case in (cases if cases is not None else self.cases)
                ],
            }
        )

    def _finished_run(self, results, tester=None):
        """Run finished with the given results, one per case."""
        run = self._create_run(tester=tester)
        run.action_start()
        for line, result in zip(run.line_ids, results, strict=True):
            line.write({"result": result, "comment": "Checked"})
        run.action_done()
        return run

    # qa.functional.area
    def test_area_two_levels_only(self):
        child = self.env["qa.functional.area"].create(
            {"name": "Child", "parent_id": self.area.id}
        )
        with self.assertRaisesRegex(ValidationError, "two levels deep only"):
            self.env["qa.functional.area"].create(
                {"name": "Grandchild", "parent_id": child.id}
            )
        self.assertEqual(child.display_name, "Test Area / Child")

    # qa.tag
    @mute_logger("odoo.sql_db")
    def test_tag_name_unique(self):
        self.env["qa.tag"].create({"name": "smoke-test"})
        with self.assertRaises(IntegrityError):
            self.env["qa.tag"].create({"name": "smoke-test"})

    # qa.requirement
    def test_requirement_coverage(self):
        requirement = self.env["qa.requirement"].create(
            {"name": "Requirement", "area_id": self.area.id}
        )
        self.assertEqual(requirement.case_count, 0)
        not_covered = self.env["qa.requirement"].search([("case_ids", "=", False)])
        self.assertIn(requirement, not_covered)
        requirement.case_ids = [Command.link(self.cases[0].id)]
        self.assertEqual(requirement.case_count, 1)
        self.assertIn(requirement, self.cases[0].requirement_ids)

    # qa.test.case
    def test_case_run_stats(self):
        self._finished_run(["pass", "pass", "pass"])
        self._finished_run(["fail", "pass", "pass"])
        case = self.cases[0]
        self.assertEqual(case.run_count, 2)
        self.assertEqual(case.last_result, "fail")

    # qa.test.run: state machine
    def test_run_cannot_start_without_lines(self):
        run = self._create_run(cases=self.env["qa.test.case"])
        with self.assertRaisesRegex(UserError, "Add at least one test case"):
            run.action_start()

    def test_run_cannot_jump_from_draft_to_done(self):
        run = self._create_run()
        with self.assertRaisesRegex(UserError, "Only a running run can be finished"):
            run.action_done()
        self.assertEqual(run.state, "draft")

    def test_run_done_needs_all_results(self):
        run = self._create_run()
        run.action_start()
        run.line_ids[0].result = "pass"
        with self.assertRaisesRegex(ValidationError, "every line needs a result"):
            run.action_done()

    def test_run_counts_and_verdict(self):
        run = self._finished_run(["pass", "fail", "pass"])
        self.assertEqual(run.state, "done")
        self.assertTrue(run.date_end)
        self.assertEqual((run.pass_count, run.fail_count, run.todo_count), (2, 1, 0))
        self.assertAlmostEqual(run.pass_rate, 66.67, places=2)
        self.assertEqual(run.verdict, "fail")
        self.assertEqual(run.estimate_minutes, 30)

    # qa.test.run.line
    def test_line_fail_needs_comment(self):
        run = self._create_run()
        run.action_start()
        with self.assertRaisesRegex(ValidationError, "Explain why case"):
            run.line_ids[0].action_set_fail()

    def test_line_locked_after_done(self):
        run = self._finished_run(["pass", "pass", "pass"])
        with self.assertRaisesRegex(UserError, "cannot be changed"):
            run.line_ids[0].write({"result": "fail"})
        with self.assertRaisesRegex(UserError, "cannot be changed"):
            run.line_ids.unlink()

    # qa.retest.wizard
    def test_retest_wizard_takes_failed_cases_only(self):
        run = self._finished_run(["fail", "pass", "fail"])
        wizard = (
            self.env["qa.retest.wizard"]
            .with_context(active_id=run.id, active_model="qa.test.run")
            .create({})
        )
        self.assertEqual(wizard.case_ids, self.cases[0] | self.cases[2])
        action = wizard.action_create_run()
        new_run = self.env["qa.test.run"].browse(action["res_id"])
        self.assertEqual(new_run.state, "draft")
        self.assertEqual(new_run.line_ids.case_id, self.cases[0] | self.cases[2])
        self.assertEqual(new_run.task_id, self.task)

    # project.task and res.users extensions
    def test_task_and_user_counters(self):
        self._finished_run(["pass", "pass", "pass"])
        self._create_run()
        self.assertEqual(self.task.qa_run_count, 2)
        self.assertEqual(self.task.qa_verdict, "pass")
        self.assertEqual(self.tester.qa_open_run_count, 1)

    # security
    def test_tester_sees_fewer_runs_than_lead(self):
        own_run = self._create_run(tester=self.tester)
        other_run = self._create_run(tester=self.other_tester)
        runs_as_tester = self.env["qa.test.run"].with_user(self.tester).search([])
        runs_as_lead = self.env["qa.test.run"].with_user(self.lead).search([])
        self.assertLess(len(runs_as_tester), len(runs_as_lead))
        self.assertIn(own_run, runs_as_tester)
        self.assertNotIn(other_run, runs_as_tester)
        self.assertIn(other_run, runs_as_lead)
        with self.assertRaises(AccessError):
            other_run.with_user(self.tester).read(["name"])

    def test_tester_cannot_edit_reference_data(self):
        with self.assertRaises(AccessError):
            self.env["qa.tag"].with_user(self.tester).create({"name": "new tag"})
        self.env["qa.tag"].with_user(self.lead).create({"name": "new tag"})
