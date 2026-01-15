from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS

import logging
_logging = _logger = logging.getLogger(__name__)

class AuthSignupHomeInherited(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        login = kw.get('login')
        response = super().web_auth_signup(*args, **kw)

        user_id = request.env['res.users'].search([
                ('login', '=', login)
            ])
        signup_token = request.session.session_token
        if len(user_id) == 1 and signup_token not in [None,False,""]:
            user_id.sudo().partner_id.signup_token = signup_token

        if len(user_id) == 1 and user_id.email_verified == False:
            _logger.info(f"DEF25 user_id: {user_id} {user_id.name}")
            return request.redirect('/web/session/logout?redirect=/web/check_email')
        return response

    def web_auth_reset_password(self, *args, **kw):
        kw_token = kw.get('token')
        kw_login = kw.get('login')
        _logger.info(f"DEF12 kw_token: {kw_token} kw_login: {kw_login} ============")
        if kw_token not in [None, False, ""] and kw_login not in [None, False, ""] :
            request.env.user.email_verified = True
            _logger.info(f"    ==== user_id: {request.env.user} {request.env.user.name} email_verified: {request.env.user.email_verified}")
        else:
            pass
        
        return super().web_auth_reset_password(*args, **kw)