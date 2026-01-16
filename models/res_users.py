from odoo import models, fields, api
from odoo.http import request

from odoo.addons.auth_signup.models.res_partner import random_token

from odoo.exceptions import ValidationError

import logging
_logging = _logger = logging.getLogger(__name__)

class ResUsersInherited(models.Model):
    _inherit = 'res.users'

    email_verified = fields.Boolean(default=False)
    
    def _is_ip_address_blocked(self,ip_address):
        output = False
        key_name = "ip_address_blocked"
        key_default_value = "99.99.99.99"
        
        ir_config_parameter_id = self.env['ir.config_parameter'].sudo().search([
            ('key', '=', key_name)
        ])
        if len(ir_config_parameter_id) == 0:
            _logger.info(f"    ==== Adding default record value for ")
            ir_config_parameter_id = ir_config_parameter_id.create({
                'key': key_name,
                'value': key_default_value
            })
        elif len(ir_config_parameter_id) == 1:
            try:
                ip_address_blocked = str(ir_config_parameter_id.value).replace(" ", "").split(",")
            except:
                ip_address_blocked = [ir_config_parameter_id.value]
            if ip_address in ip_address_blocked:
                output = True
            else: 
                output = False
        elif len(ir_config_parameter_id) > 1:
            raise ValidationError(f"Duplicated key values in system parameters for: {key_name}")
        else:
            pass
        
        return output

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info(f"    ==== create user generating token")
        
        user_ids = super().create(vals_list)
        self._set_partner_id_signup_token( user_ids )
        
        return user_ids
    
    def _set_partner_id_signup_token(self, user_ids):
        for user_id in user_ids:
            if user_id.signup_token in [None, False, ""]:
                signup_token = random_token()
                user_id.sudo().partner_id.signup_token = signup_token
        return