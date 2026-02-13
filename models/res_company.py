from odoo import models, fields, api

class ResCompanyInherited(models.Model):
    _inherit = 'res.company'

    email_verification = fields.Boolean()
    email_verification_delay = fields.Integer(default=5)
    ip_address_verification = fields.Boolean()
    payment_transaction_error_qty = fields.Integer(default=3)
    payment_transaction_user_blocked_time_min = fields.Integer(default=1)