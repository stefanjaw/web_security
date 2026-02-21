from odoo import http
from odoo.addons.payment.controllers.portal import PaymentPortal
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_partner import random_token

from datetime import datetime, timedelta

from odoo.exceptions import ValidationError

from odoo.http import request, route

import requests

import re

import logging
_logger = logging.getLogger(__name__)

class PaymentPortalInherited(PaymentPortal):
    
    @route(
        '/shop/payment/transaction/<int:order_id>', type='json', auth='public', website=True
    )    
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        _logger.info(f"    ==== shop_payment_transaction")
        
        if kwargs.get('verify_email_action'):
            return self._email_verification( **kwargs )
        
        error_msg = self._user_last_sale_orders_ok( ).get('error')
        if error_msg:
            raise ValidationError( error_msg )
        
        return super().shop_payment_transaction(order_id, access_token, **kwargs)

    def _user_last_sale_orders_ok(self):
        payment_transaction_error_qty = request.env.company.payment_transaction_error_qty
        
        payment_transaction_user_blocked_time_min = request.env.company.payment_transaction_user_blocked_time_min
        
        error_status = ['draft','pending','cancel','error']
        user_id = request.env.user
        from_create_date = datetime.utcnow() - timedelta(minutes=payment_transaction_user_blocked_time_min)
        
        payment_transaction_ids_errors = request.env['payment.transaction'].sudo().search([
            ('partner_id','=', user_id.partner_id.id),
            ('create_date','>=', from_create_date),
            ('state','in',error_status)
        ])
        
        result = {}
        if len(payment_transaction_ids_errors) >= payment_transaction_error_qty:
            msg1 = f"Your account has been temporarily locked due to multiple failed payment attempts.\nPlease wait at least {payment_transaction_user_blocked_time_min} minute(s) before trying again."
            result['error'] = msg1
        
        return result
    
    def _email_verification(self, **kwargs):
        _logger.info(f"    ==== _email_verification")
        login_email_template_id = request.env.ref('auth_signup.mail_template_user_signup_account_created')
        if len(login_email_template_id) != 1:
            raise ValidationError("Login Email Template Not Found")
        
        user_id = request.env.user
        
        email_verified = user_id.email_verified
        if email_verified == True:
            
            return {    'email_verified': email_verified,
                        'btn_txt': 'OK',
                        'message': 'Email Verified',
                        'verify_email_action': 'refresh'
                   }
        else:
            pass

        verify_email_action = kwargs.get('verify_email_action')
        
        if verify_email_action == "verify_email":
            
            user_id.sudo().partner_id.signup_token = random_token()
            
            result = login_email_template_id.sudo().send_mail(user_id.id, force_send=True)
            
            message = f"Check your email & click on the provided link to verify your email address. To get help, please call: {request.env.company.phone}"
            
            data = {'btn_txt': 'Refresh',
                    'message': f'{message}',
                    'verify_email_action': 'refresh',
                    'email_verification_delay': request.env.company.email_verification_delay
                   }
        else:
            message = f"Check your email & click on the provided link to verify your email address. To get help, please call: {request.env.company.phone}"
            
            data = {'btn_txt': 'Refresh',
                    'message': f'{message}',
                    'verify_email_action': 'refresh',
                    'email_verification_delay': request.env.company.email_verification_delay
                   }
        return data
