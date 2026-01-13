from odoo import models, fields, api
from odoo.http import request

from odoo.exceptions import ValidationError

import logging
_logging = _logger = logging.getLogger(__name__)

class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'

    BLOCK_MESSAGE = "Not Allowed record"
    
    # @api.model_create_multi 
    # def create(self, vals_list):
    #     _logger.info(f"    ==== create")
        
    #     ip_address = request.httprequest.environ['REMOTE_ADDR']
    #     if self.env['res.users'].sudo()._is_ip_address_blocked(ip_address) == True:
    #         msg1 = f"create: {self.BLOCK_MESSAGE}"
    #         _logger.info(f"        ==== Blocking {ip_address}: {msg1}")
    #         raise ValidationError( msg1 )
    #     else:
    #         pass
    #     _logger.info(f"DEF25    ==== _login")
    #     _logger.info(f"DEF26 url: {request.httprequest.url}")
    #     user_id = self.env.user
    #     if user_id.id == 4: # Public User
    #         for vals in vals_list:
    #             vals['active'] = False
    #     _logger.info(f"DEF27        ==== ip_address: {ip_address} user_id: {user_id} {user_id.name}\n{vals_list}")            
    #     # STOPCREATE
    #     return super().create(vals_list)

    # def write(self, vals):
    #     _logger.info(f"    ==== write")
    #     ip_address = request.httprequest.environ['REMOTE_ADDR']
    #     if self.env['res.users'].sudo()._is_ip_address_blocked(ip_address) == True:
    #         msg1 = f"write: {self.BLOCK_MESSAGE}"
    #         _logger.info(f"        ==== Blocking {ip_address}: {msg1}")
    #         raise ValidationError( msg1 )
    #     else:
    #         pass

    #     return super().write(vals)
