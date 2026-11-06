from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestHrHospital(TransactionCase):
    """Business rules of block 3 and the access ladder of block 6."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_intern = cls.env["hospital.doctor.category"].create(
            {"name": "Test Intern", "is_internship": True}
        )
        cls.category_doctor = cls.env["hospital.doctor.category"].create(
            {"name": "Test Specialist"}
        )

        def user(login, group):
            return new_test_user(cls.env, login=login, groups=f"hr_hospital.{group}")

        cls.user_patient = user("t_patient", "group_hospital_patient")
        cls.user_intern = user("t_intern", "group_hospital_intern")
        cls.user_doctor = user("t_doctor", "group_hospital_doctor")
        cls.user_other_doctor = user("t_other_doctor", "group_hospital_doctor")
        cls.user_manager = user("t_manager", "group_hospital_manager")
        cls.user_admin = user("t_admin", "group_hospital_admin")

        Doctor = cls.env["hr.hospital.doctor"]
        cls.doctor = Doctor.create(
            {
                "name": "Mentor",
                "category_id": cls.category_doctor.id,
                "user_id": cls.user_doctor.id,
            }
        )
        cls.other_doctor = Doctor.create(
            {
                "name": "Other Doctor",
                "category_id": cls.category_doctor.id,
                "user_id": cls.user_other_doctor.id,
            }
        )
        cls.intern = Doctor.create(
            {
                "name": "Intern",
                "category_id": cls.category_intern.id,
                "mentor_id": cls.doctor.id,
                "user_id": cls.user_intern.id,
            }
        )
        Patient = cls.env["hr.hospital.patient"]
        cls.patient = Patient.create({"name": "Own", "user_id": cls.user_patient.id})
        cls.other_patient = Patient.create({"name": "Stranger"})

        Visit = cls.env["hr.hospital.visit"]
        cls.visit_doctor = Visit.create(
            {"doctor_id": cls.doctor.id, "patient_id": cls.patient.id}
        )
        cls.visit_intern = Visit.create(
            {"doctor_id": cls.intern.id, "patient_id": cls.other_patient.id}
        )
        cls.visit_other = Visit.create(
            {"doctor_id": cls.other_doctor.id, "patient_id": cls.other_patient.id}
        )
        cls.all_visits = cls.visit_doctor | cls.visit_intern | cls.visit_other

    def _visible_visits(self, user):
        """Test visits that ``user`` can find through the record rules."""
        Visit = self.env["hr.hospital.visit"].with_user(user)
        return Visit.search([("id", "in", self.all_visits.ids)])

    # --- block 3: doctor -------------------------------------------------

    def test_compute_is_intern(self):
        """is_intern follows the Internship flag of the doctor's category."""
        self.assertTrue(self.intern.is_intern)
        self.assertFalse(self.doctor.is_intern)
        self.intern.category_id = self.category_doctor
        self.assertFalse(self.intern.is_intern)
        self.category_doctor.is_internship = True
        self.assertTrue(self.doctor.is_intern)

    def test_check_is_intern_mentor(self):
        """An intern cannot be chosen as a mentor."""
        with self.assertRaises(ValidationError) as error:
            self.other_doctor.mentor_id = self.intern
        self.assertIn("intern cannot be a mentor", str(error.exception))
        self.other_doctor.mentor_id = self.doctor
        self.assertEqual(self.other_doctor.mentor_id, self.doctor)

    # --- block 3: visit --------------------------------------------------

    def test_visit_done_cannot_be_changed(self):
        """A done visit keeps its date and doctor, and cannot be archived."""
        new_date = fields.Datetime.now() + timedelta(days=3)
        self.visit_doctor.planned_date = new_date
        self.assertEqual(self.visit_doctor.planned_date, new_date)
        self.visit_doctor.state = "done"
        with self.assertRaises(ValidationError) as error:
            self.visit_doctor.doctor_id = self.other_doctor
        self.assertIn("cannot be edited", str(error.exception))
        with self.assertRaises(ValidationError) as error:
            self.visit_doctor.active = False
        self.assertIn("cannot be archived", str(error.exception))

    def test_visit_done_cannot_be_deleted(self):
        """A done visit cannot be deleted; a planned one can."""
        self.visit_doctor.state = "done"
        with self.assertRaises(ValidationError) as error:
            self.visit_doctor.unlink()
        self.assertIn("cannot be deleted", str(error.exception))
        self.visit_other.unlink()
        self.assertFalse(self.visit_other.exists())

    # --- block 3: disease ------------------------------------------------

    def test_disease_complete_name_and_cycle(self):
        """complete_name shows the path; a disease cannot be its own ancestor."""
        Disease = self.env["hr.hospital.disease"]
        parent = Disease.create({"name": "Infectious"})
        child = Disease.create({"name": "Viral", "parent_id": parent.id})
        self.assertEqual(child.complete_name, "Infectious / Viral")
        self.assertEqual(child.display_name, "Infectious / Viral")
        with self.assertRaises(ValidationError) as error:
            parent.parent_id = child
        self.assertIn("cannot be its own parent", str(error.exception))

    # --- block 6: access ladder -----------------------------------------

    def test_patient_sees_only_own_visits(self):
        """A patient reads only own visits and cannot change them."""
        self.assertEqual(self._visible_visits(self.user_patient), self.visit_doctor)
        with self.assertRaises(AccessError):
            self.visit_doctor.with_user(self.user_patient).description = "x"

    def test_intern_sees_and_edits_own_visits(self):
        """An intern sees and edits own visits, but not the mentor's ones."""
        self.assertEqual(self._visible_visits(self.user_intern), self.visit_intern)
        self.visit_intern.with_user(self.user_intern).description = "checked"
        self.assertEqual(self.visit_intern.description, "checked")
        with self.assertRaises(AccessError):
            self.visit_doctor.with_user(self.user_intern).description = "x"

    def test_doctor_sees_own_and_interns_visits(self):
        """A doctor sees own visits and visits of own interns only."""
        self.assertEqual(
            self._visible_visits(self.user_doctor),
            self.visit_doctor | self.visit_intern,
        )
        self.visit_intern.with_user(self.user_doctor).description = "by mentor"
        with self.assertRaises(AccessError):
            self.visit_other.with_user(self.user_doctor).description = "x"

    def test_manager_sees_all_but_cannot_delete(self):
        """A manager sees every visit, but deletion is denied by the ACL."""
        self.assertEqual(self._visible_visits(self.user_manager), self.all_visits)
        with self.assertRaises(AccessError):
            self.visit_other.with_user(self.user_manager).unlink()

    def test_admin_can_delete(self):
        """The module administrator can delete any planned visit."""
        self.visit_other.with_user(self.user_admin).unlink()
        self.assertFalse(self.visit_other.exists())

    def test_user_outside_ladder_has_no_access(self):
        """An internal user outside the hospital groups cannot read visits."""
        plain = new_test_user(self.env, login="t_plain", groups="base.group_user")
        with self.assertRaises(AccessError):
            self.env["hr.hospital.visit"].with_user(plain).search([])
