from odoo import models, fields

class Doctor(models.Model):
    _name = "hms.doctor"
    _rec_name = "first_name"

    first_name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    image = fields.Image(string="Image")
    doctor_id = fields.Many2many(comodel_name="hms.patient")