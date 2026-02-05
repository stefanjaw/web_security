from odoo import models, fields, api

class ResCompanyInherited(models.Model):
    _inherit = 'res.company'

    email_verification = fields.Boolean()
    email_verification_delay = fields.Integer(default=5)
    ip_address_verification = fields.Boolean()