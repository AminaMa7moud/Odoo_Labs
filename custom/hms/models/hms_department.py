from odoo import models, fields

class Department(models.Model):
    _name = 'hms.department'

    name = fields.Char(string="Department Name", required=True)
    capacity = fields.Integer(string="Capacity", required=True)
    is_opened = fields.Boolean(string="Is Opened")

    patient_id = fields.One2many(comodel_name='hms.patient', inverse_name='department_id')

