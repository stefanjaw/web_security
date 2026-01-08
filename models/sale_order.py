from odoo import models, fields, api
from odoo.http import request

from odoo.exceptions import ValidationError

import logging
_logging = _logger = logging.getLogger(__name__)

class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'

    BLOCK_MESSAGE = "Not Allowed record"
    
    @api.model_create_multi 
    def create(self, vals_list):
        _logger.info(f"    ==== create")
        ip = request.httprequest.environ['REMOTE_ADDR']
        if self.env['res.users'].sudo()._is_ip_address_blocked(ip) == True:
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
        if self.env['res.users'].sudo()._is_ip_address_blocked(ip) == True:
            msg1 = f"write: {self.BLOCK_MESSAGE}"
            _logger.info(f"        ==== Blocking {ip}: {msg1}")
            raise ValidationError( msg1 )
        else:
            pass

        return super().write(vals)
