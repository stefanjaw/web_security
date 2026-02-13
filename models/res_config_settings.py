from odoo import models, fields, api
from odoo.addons.base_setup.models.res_config_settings import ResConfigSettings

import logging
_logging = _logger = logging.getLogger(__name__)

class ResConfigSettingsInherited(ResConfigSettings):
    _inherit = 'res.config.settings'
    
    email_verification = fields.Boolean(related="company_id.email_verification",readonly=False)
    email_verification_delay = fields.Integer(related="company_id.email_verification_delay",readonly=False)
    ip_address_verification = fields.Boolean(related="company_id.ip_address_verification",readonly=False)
    
    payment_transaction_error_qty = fields.Integer(
            related="company_id.payment_transaction_error_qty",readonly=False
        )
    payment_transaction_user_blocked_time_min = fields.Integer(
            related="company_id.payment_transaction_user_blocked_time_min",readonly=False
        )

    def open_ip_address_blocked(self):
        _logger.info(f"    ==== open_ip_address_blocked")
        return {
            'type': 'ir.actions.act_window',
            'name': 'System Parameters',
            'res_model': 'ir.config_parameter',
            'view_mode': 'tree,form',
            'domain': [('key', '=', 'ip_address_blocked')],
            'target': 'main',  # main or new
        }