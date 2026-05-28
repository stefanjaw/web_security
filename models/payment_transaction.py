# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import _, models
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_processing_values(self, processing_values):
        _logger.info(f"DEF12 _get_specific_processing_values ===")
        user_id = self.env.user
        if user_id.email_verified == False:
            # raise ValidationError(f"User email: {user_id.login} is not verified !!")
            pass
        elif user_id.id == 4: # Public User
            raise ValidationError("User is not logged in")
        
        res = super()._get_specific_processing_values(processing_values)
        
        return res

        