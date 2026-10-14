import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MassReassignDoctorWizard(models.TransientModel):
    _name = "mass.reassign.doctor.wizard"
    _description = "Mass Reassign Personal Doctor"

    patient_ids = fields.Many2many(
        comodel_name="hr.hospital.patient",
        string="Patients",
    )
    new_doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="New Doctor",
        required=True,
    )
    change_date = fields.Date(
        string="Change Date",
        default=fields.Date.context_today,
    )

    @api.model
    def default_get(self, fields_list):
        """Pre-fill patients selected in the list the wizard was opened from."""
        res = super().default_get(fields_list)
        context = self.env.context
        if context.get("active_model") == "hr.hospital.patient":
            res["patient_ids"] = [(6, 0, context.get("active_ids", []))]
        return res

    def action_reassign(self):
        """Close the current history line of each patient and open a new one."""
        self.ensure_one()
        history_model = self.env["hospital.doctor.history"]
        for patient in self.patient_ids:
            current = history_model.search(
                [("patient_id", "=", patient.id), ("active", "=", True)]
            )
            current.write({"change_date": self.change_date, "active": False})
            history_model.create(
                {
                    "patient_id": patient.id,
                    "doctor_id": self.new_doctor_id.id,
                    "assign_date": self.change_date,
                }
            )
            patient.personal_doctor_id = self.new_doctor_id
        return {"type": "ir.actions.act_window_close"}
