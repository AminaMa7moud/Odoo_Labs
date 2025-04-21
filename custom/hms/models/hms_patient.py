from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class Patient(models.Model):
    _name = 'hms.patient'
    _description = 'Patient'

    first_name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    birth_date = fields.Date(string="Birth Date", required=True)
    history = fields.Html(string="History")
    cr_ratio = fields.Float(string="CR Ratio")
    blood_type = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ], string="Blood Type")
    pcr = fields.Boolean(string="PCR Done")
    image = fields.Image(string="Image")
    address = fields.Text(string="Address")
    age = fields.Integer(string="Age", compute="_compute_age", store=True)
    states = fields.Selection([
        ("Undetermined", "Undetermined"),
        ("Good", "Good"),
        ("Fair", "Fair"),
        ("Serious", "Serious")
    ], string="states")
    department_id = fields.Many2one(comodel_name='hms.department')
    doctor_ids = fields.Many2many(comodel_name='hms.doctor')
    department_capacity = fields.Integer(string='Department Capacity', compute='_compute_department_capacity', store=False)
    log_ids = fields.One2many('hms.log.history', 'patient_id', string='Log History')
    email = fields.Char(string="Email", required=True)
    _sql_constraints = [
            ('unique_email', 'UNIQUE(email)', 'This email address is already used.')
        ]
    @api.constrains('email')
    def _check_unique_email(self):
        for record in self:
            if record.email:
                if '@' not in record.email or '.' not in record.email:
                    raise ValidationError("Please enter a valid email address (e.g., eman@eman.com).")


    def action_state(self):
        for rec in self:
            if rec.states == 'Undetermined':
                rec.states = 'Good'
            elif rec.states == 'Good':
                rec.states = 'Fair'
            elif rec.states == 'Fair':
                rec.states = 'Serious'
            else:
                rec.states = 'Undetermined'

    @api.depends('birth_date')
    def _compute_age(self):
        for rec in self:
            if rec.birth_date:
                today = date.today()
                rec.age = today.year - rec.birth_date.year - (
                    (today.month, today.day) < (rec.birth_date.month, rec.birth_date.day)
                )
                if rec.age < 30:
                    rec.pcr = True
                    return {
                        'warning': {
                            'title': "PCR Checked Automatically",
                            'message': "PCR has been automatically checked because the age is under 30.",
                        }
                    }
    @api.depends('department_id')
    def _compute_department_capacity(self):
        for patient in self:
            patient.department_capacity = patient.department_id.capacity if patient.department_id else 0

        
    def create_log_entry(self, description, created_by='System'):
        self.env['hms.log.history'].create({
            'patient_id': self.id,
            'created_by': created_by,
            'description': description,
        })

    @api.model
    def write(self, vals):
        """Override write to log states changes."""
        res = super(Patient, self).write(vals)
        if 'states' in vals:
            states_name = dict(self._fields['states'].selection).get(vals['states'], vals['states'])
            self.create_log_entry(
                description=f'states changed to {states_name}',
                created_by='System'
            )
        return res
    
    @api.onchange('pcr')
    def _onchange_pcr_cr_ratio(self):
        for rec in self:
            if rec.pcr and not rec.cr_ratio:
                return {
                    'warning': {
                        'title': "CR Ratio Required",
                        'message': "Please enter the CR Ratio when PCR is checked.",
                    }
                }
    @api.model
    def write(self, vals):
        """Override write to log state changes."""
        res = super(Patient, self).write(vals)
        if 'states' in vals:
            state_name = dict(self._fields['states'].selection).get(vals['states'], vals['states'])
            self.create_log_entry(
                description=f'State changed to {state_name}',
                created_by='System'
            )
        return res
    

