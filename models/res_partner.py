from odoo import models, fields, api
from odoo.http import request

from odoo.exceptions import ValidationError

import logging
_logging = _logger = logging.getLogger(__name__)

class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'

    BLOCK_MESSAGE = "Not Allowed contact record"

    @api.model_create_multi 
    def create(self, vals_list):
        _logger.info(f"    ==== create")
        ip = request.httprequest.environ['REMOTE_ADDR']
        if self._is_ip_address_blocked(ip) == True:
            _logger.info(f"DEF19    ==== _login")
            msg1 = f"create: {self.BLOCK_MESSAGE}"
            _logger.info(f"        ==== Blocking {ip}: {msg1}")
            raise ValidationError( msg1 )
        else:
            pass
        _logger.info(f"DEF25    ==== _login")        
        return super().create(vals_list)

    def write(self, vals):
        _logger.info(f"    ==== write")
        ip = request.httprequest.environ['REMOTE_ADDR']
        if self._is_ip_address_blocked(ip) == True:
            _logger.info(f"DEF32    ==== _login")
            msg1 = f"write: {self.BLOCK_MESSAGE}"
            _logger.info(f"        ==== Blocking {ip}: {msg1}")
            raise ValidationError( msg1 )
        else:
            pass
        _logger.info(f"DEF25    ==== _login")        
        return super().write(vals)
    
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
