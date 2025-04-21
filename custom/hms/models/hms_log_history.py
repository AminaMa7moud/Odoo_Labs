from odoo import models, fields

class LogHistory(models.Model):
    _name = "hms.log.history"
    _description = "Log History"

    created_by = fields.Char(string="Created By", default="System", readonly=True)
    date = fields.Datetime(string="Date", default=fields.Datetime.now, readonly=True)
    description = fields.Text(string="Description", required=True)
    patient_id = fields.Many2one(comodel_name="hms.patient", string="Patient", required=True)