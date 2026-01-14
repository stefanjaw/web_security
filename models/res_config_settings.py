from odoo import models, fields, api
from odoo.addons.base_setup.models.res_config_settings import ResConfigSettings

import logging
_logging = _logger = logging.getLogger(__name__)

class ResConfigSettingsInherited(ResConfigSettings):
    _inherit = 'res.config.settings'
    
    email_verification = fields.Boolean()
    ip_address_verification = fields.Boolean()

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