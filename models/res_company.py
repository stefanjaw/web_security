from odoo import models, fields, api

class ResCompanyInherited(models.Model):
    _inherit = 'res.company'

    email_verification = fields.Boolean()
    ip_address_verification = fields.Boolean()