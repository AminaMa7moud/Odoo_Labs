from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CrmCustomer(models.Model):
    _inherit = "res.partner"
    _description = 'CRM Customer'

    custom_field = fields.Char(string='Custom Field')
    related_patient_id = fields.Many2one('hms.patient', string="Related Patient")
    vat = fields.Char(string='Tax ID', required=True)

    def unlink(self):
        for record in self:
            if record.related_patient_id:
                raise ValidationError(
                    _("Cannot delete customer '%s' because it is linked to a patient.") % record.name
                )
        return super(CrmCustomer, self).unlink()

    @api.constrains('email')
    def _check_unique_email_against_patients(self):
        for record in self:
            if record.email:
                email = record.email.strip()
                patient = self.env['hms.patient'].search([('email', '=', email)], limit=1)
                if patient:
                    first_name = patient.first_name or "Unknown Patient"
                    raise ValidationError(
                        _("The email '%s' is already used by a patient: %s. "
                          "Please use a different email for this customer.") % (record.email, patient.display_name)
                    )