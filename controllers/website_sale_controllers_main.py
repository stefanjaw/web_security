from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers.portal import PaymentPortal # V19
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_partner import random_token

from datetime import datetime, timedelta

from odoo.exceptions import ValidationError

from odoo.http import request

import requests

import re

import logging
_logger = logging.getLogger(__name__)

class PaymentPortalInherited(PaymentPortal):
    
    @http.route(
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

class WebsiteSaleInherited(WebsiteSale):
    
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def shop_address(self, **kw):
        _logger.info(f"    ==== /shop/address")


        user_int = request.session.uid
        if user_int:
            return super().shop_address(**kw)
        
        user_id = False        
        email = kw.get('email')
        password = kw.get('password')
        name = kw.get('name')
        
        group_portal_id = request.env.ref('base.group_portal')
        if len(group_portal_id) != 1:
            raise ValidationError("Group Portal Not Found")
        
        login_email_template_id = request.env.ref('auth_signup.mail_template_user_signup_account_created')
        if len(login_email_template_id) != 1:
            raise ValidationError("Login Email Template Not Found")
        
        if email and password and name:
            
            key_names = ['name', 'lastname','email','street','street2','password',
                         'vat','phone','company_name','city','zip','country_id','state_id'
                        ]
            kw_filtered = {key: kw.get(key) for key in key_names if key in kw}
            kw_filtered['login'] = email
            kw_filtered['groups_id'] = [(6,0,[group_portal_id.id])]
            
            try:
                user_id = request.env['res.users'].sudo().with_context(no_reset_password=True,create_user=True).create(kw_filtered)
                request.env.cr.commit()
                _logger.info(f"    ==== Created user_id: {user_id}")
                
                result = login_email_template_id.sudo().send_mail(user_id.id, force_send=True)
                
                user_int = request.session.authenticate(
                    request.db,
                    email,
                    password
                )
            
            except Exception as e:
                _logger.info(f"    ==== Error creating user: {e}")
                
                request.env.cr.rollback()
                
                reset_value = False
                request.params['email'] = kw['email'] = reset_value
                request.params['password'] = kw['password'] = reset_value
                request.params['error'] = kw['error'] = f"{e} \t{email}"
                
                return super().shop_address(**kw)
        
        return super().shop_address(**kw)
    
    def checkout_form_validate(self, mode, all_form_values, data):
        _logger.info(f"    ==== checkout_form_validate")
        
        error, error_msg = super().checkout_form_validate(mode, all_form_values, data)
        
        if request.env.user.id == 4: #4 public user
            user_id = []
        else:
            user_id = request.env.user
        
        if all_form_values.get('password') in ['', False, None] \
        and "billing" in all_form_values.get('mode') \
        and len(user_id) == 0:
            error['password'] = 'missing'
            error_msg.append('Password is required')
        
        return error, error_msg
