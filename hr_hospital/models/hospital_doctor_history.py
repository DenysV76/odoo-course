import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class HospitalDoctorHistory(models.Model):
    _name = "hospital.doctor.history"
    _description = "Personal Doctor History"
    _order = "assign_date desc, id desc"

    patient_id = fields.Many2one(
        comodel_name="hr.hospital.patient",
        string="Patient",
        required=True,
    )
    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Doctor",
        required=True,
    )
    assign_date = fields.Date(
        string="Assignment Date",
        required=True,
        default=fields.Date.context_today,
    )
    change_date = fields.Date(string="Doctor Change Date")
    active = fields.Boolean(default=True)

    @api.onchange("assign_date", "change_date")
    def _onchange_assign_date(self):
        if (
            self.assign_date
            and self.change_date
            and self.assign_date > self.change_date
        ):
            return {
                "warning": {
                    "title": "Увага",
                    "message": "Дата зміни лікаря не може бути раніше ніж дата призначення",
                }
            }

    # TODO(1.7): _compute_display_name + _rec_names_search
