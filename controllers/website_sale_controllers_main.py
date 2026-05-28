from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_partner import random_token

from datetime import datetime, timedelta

from odoo.exceptions import ValidationError

from odoo.http import request, route

import requests

import re

import logging
_logger = logging.getLogger(__name__)


class WebsiteSaleInherited(WebsiteSale):
    
    @route(
        '/shop/address/submit', type='http', methods=['POST'], auth='public', website=True,
        sitemap=False
    )
    def shop_address_submit( 
        self,
        partner_id=None,
        address_type='billing',
        use_delivery_as_billing=None,
        callback=None,
        **form_data
    ):
        _logger.info(f"    ==== shop_address_submit")
        user_int = request.session.uid
        if user_int:
            return super().shop_address_submit(
                partner_id,
                address_type,
                use_delivery_as_billing,
                callback,
                **form_data
            )
        
        user_id = False        
        email = form_data.get('email')
        password = form_data.get('password')
        name = form_data.get('name')
        
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
            form_data_filtered = {key: form_data.get(key) for key in key_names if key in form_data}
            form_data_filtered['login'] = email
            form_data_filtered['group_ids'] = [(6,0,[group_portal_id.id])]
            _logger.info(f"DEF73 form_data_filtered: \n\t{form_data_filtered}")
            try:
                user_id = request.env['res.users'].sudo().with_context(no_reset_password=True,create_user=True).create(form_data_filtered)
                request.env.cr.commit()
                _logger.info(f"    ==== Created user_id: {user_id}")
                result = login_email_template_id.sudo().send_mail(user_id.id, force_send=True)
                user_int = request.session.authenticate(
                    request.env,
                    {   'login': email,
                        'password': password,
                        'type': 'password'
                    }
                )
            except Exception as e:
                _logger.info(f"    ==== Error creating user: {e}")
                
                request.env.cr.rollback()
                
                reset_value = False
                request.params['email'] = form_data['email'] = reset_value
                request.params['password'] = form_data['password'] = reset_value
                request.params['error'] = form_data['error'] = f"{e} \t{email}"
                return super().shop_address_submit(
                        partner_id,
                        address_type,
                        use_delivery_as_billing,
                        callback,
                        **form_data
                    )
        
        return super().shop_address_submit(
                    partner_id,
                    address_type,
                    use_delivery_as_billing,
                    callback,
                    **form_data
                )
    
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
