from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS

from markupsafe import Markup

import logging
_logging = _logger = logging.getLogger(__name__)

class AuthSignupHomeInherited(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        _logger.info(f"    ==== /web/signup web_auth_signup ============")
        login = kw.get('login')

        self._set_template_body_html_with_token()

        response = super().web_auth_signup(*args, **kw)

        user_id = request.env['res.users'].search([
                ('login', '=', login)
            ])
        
        return response

    def _set_template_body_html_with_token(self):
        _logger.info(f"    ==== _set_template_body_html_with_token")
        template_id = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
        if len(template_id) == 1:

            text_start = '<div style="margin: 16px 0px 16px 0px;">'
            text_end = 'Go to My Account'
            text_stop = '<!-- Modified Text -->'
            text_new = """<div style="margin: 16px 0px 16px 0px;"><!-- Modified Text -->
            
            <p style="margin:0px 0 16px 0;box-sizing:border-box;">Click the button "Go to My account" or Copy and paste the following URL into your browser:</p>
            <pre style="margin:0px 0 16px 0;box-sizing:border-box;text-wrap-mode:wrap;white-space-collapse:preserve;color:#111827;overflow-y:auto;overflow-x:auto;unicode-bidi:bidi-override;direction:ltr;font-size:13px;background-color:#f4f4f4; padding:10px; border-radius:5px; font-family: monospace;" t-out="'%sweb/login?auth_login=%s&amp;token=%s' % (request.httprequest.url_root, object.email, object.partner_id.signup_type)"></pre>  
            
                                        <a t-attf-href="/web/login?auth_login={{object.email}}&amp;token={{object.partner_id.signup_type}}" style="box-sizing:border-box;background-color: #875A7B; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">
                                            Go to My Account"""

            template_body_html = template_id.sudo().body_html
            template_body_html_str = str(template_body_html)
            
            start_index = template_body_html_str.find(text_start)
            end_index = template_body_html_str.find(text_end)
            stop_index = template_body_html_str.find(text_stop)
            
            if start_index != -1 and end_index != -1 and stop_index == -1:
                _logger.info(f"    ==== Template Text Modified | {template_id.id}: {template_id.name}")
                end_index += len(text_end)  # include text_end in replacement
                template_body_html_str = template_body_html_str[:start_index] + text_new + template_body_html_str[end_index:]
            
            body_html = Markup( template_body_html_str )

            template_id.sudo().write({
                    'body_html': Markup( template_body_html_str )
                })
        
        return
    
    @http.route()
    def web_login(self, *args, **kw):
        _logger.info(f"    ==== web_login check token")

        redirect_if_logged_in = "/"
        
        try:
            result = self._validate_url_token(kw)
            if result.get('redirect') == True and request.session.uid > 4: #4 Public User
                return request.redirect( redirect_if_logged_in )
        except:
            pass
        
        return super().web_login(*args, **kw)
    
    def _validate_url_token(self, kw):
        login = kw['auth_login']
        token = kw['token']
        
        user_ids = request.env['res.users'].sudo().search([
            ('active', '=', True),
            ('login', '=', login)
        ])
        
        if len(user_ids) == 1 and token:
            if user_ids.partner_id.signup_type == token:
                _logger.info(f"    ==== web_login Email Verified")
                user_ids.email_verified = True
                user_ids.partner_id.write({
                        "signup_type": False
                    })
                return {'redirect': True}
            else:
                _logger.info(f"    ==== web_login Email Verification Failed")
        
        return {}

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        _logger.info(f"DEF79 web_auth_reset_password")
        
        kw_token = kw.get('token')
        kw_login = kw.get('login')
        _logger.info(f"DEF12 kw_token: {kw_token} kw_login: {kw_login} ============")
        if kw_token not in [None, False, ""] and kw_login not in [None, False, ""] :
            request.env.user.email_verified = True
            _logger.info(f"    ==== user_id: {request.env.user} {request.env.user.name} email_verified: {request.env.user.email_verified}")
        else:
            pass
        
        return super().web_auth_reset_password(*args, **kw)