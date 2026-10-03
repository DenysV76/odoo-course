import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HrHospitalVisit(models.Model):
    _name = "hr.hospital.visit"
    _description = "Visit"

    state = fields.Selection(
        selection=[
            ("planned", "Planned"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="planned",
        required=True,
    )
    planned_date = fields.Datetime(
        string="Planned Date",
        default=fields.Datetime.now,
    )
    visit_date = fields.Datetime(string="Actual Visit Date")

    name = fields.Char()

    active = fields.Boolean(default=True)
    description = fields.Text()

    doctor_id = fields.Many2one(
        comodel_name="hr.hospital.doctor",
        string="Doctor",
    )
    patient_id = fields.Many2one(
        comodel_name="hr.hospital.patient",
        string="Patient",
    )
    disease_id = fields.Many2one(
        comodel_name="hr.hospital.disease",
        string="Disease",
    )
    summary = fields.Html()

    # TODO(3.5.1): заборонити змінювати planned_date, visit_date, doctor_id
    # у візиту зі state == "done" (перевизначити write)
    # TODO(3.5.2): заборонити видаляти (unlink) і архівувати (active=False)
    # візити зі state == "done"; не зламати uninstall — див. «Часті помилки» п. 4
