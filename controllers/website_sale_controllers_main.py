from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale, PaymentPortal
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

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
        if request.env.user.email_verified == False and request.env.company.email_verification == True:
            if request.env.user.id == 4:
                msg1 = "Error: Need to Sign In"
            else:
                msg1 = f"Password expired for: {request.env.user.login}\n\n\tClick the button Reset Password"
                # \n\nNeed to reset your password" 
            _logger.info(f"    ==== {msg1} {request.env.user} ")
            raise ValidationError( msg1) 

        return super().shop_payment_transaction(order_id, access_token, **kwargs)


class WebsiteSaleInherited(WebsiteSale):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        _logger.info(f"    ==== /shop/address")
        
        user_int = request.session.uid
        if user_int:
            return super().address(**kw)
        
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
                
                return super().address(**kw)
                
            _logger.info(f"DEF72 user_id: {user_id}\n")
        
        return super().address(**kw)
