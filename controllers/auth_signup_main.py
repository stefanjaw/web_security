from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request

import logging
_logging = _logger = logging.getLogger(__name__)

class AuthSignupHomeInherited(AuthSignupHome):

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
