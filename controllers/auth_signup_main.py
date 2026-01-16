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
        login = kw.get('login')

        self._set_template_body_html_with_token()

        response = super().web_auth_signup(*args, **kw)

        user_id = request.env['res.users'].search([
                ('login', '=', login)
            ])
        signup_token = request.session.session_token
        if len(user_id) == 1 and signup_token in [None,False,""]:
            user_id.sudo().partner_id.signup_token = signup_token

        
        if len(user_id) == 1 and user_id.email_verified == False:
            # _logger.info(f"DEF25 user_id: {user_id} {user_id.name}")
            # return request.redirect('/web/session/logout?redirect=/web/check_email') # Commented didn't save the guest orders
            return request.redirect('/web/check_email')

        return response

    def _set_template_body_html_with_token(self):
        template_id = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
        if len(template_id) == 1:
            text_original = 'auth_login={{object.email}}" style='
            text_new =      'auth_login={{object.email}}&token={{object.partner_id.signup_token}}" style='
                        
            template_body_html = template_id.sudo().body_html
            template_body_html_str = str(template_body_html)
            
            if text_original in template_body_html_str:
                _logger.info(f"    ==== In Mail Template |{template_id.name}| replace\n\tFROM: |{text_original}|\n\tTO: |{text_new}|")
                template_body_html_str = template_body_html_str.replace(
                        text_original, text_new
                    )
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
            if user_ids.partner_id.signup_token == token:
                _logger.info(f"    ==== web_login Email Verified")
                user_ids.email_verified = True
                user_ids.partner_id.write({
                        "signup_token": False
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