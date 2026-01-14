from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request

import logging
_logging = _logger = logging.getLogger(__name__)

class AuthSignupHomeInherited(AuthSignupHome):

    def web_auth_reset_password(self, *args, **kw):
        result = super().web_auth_reset_password(*args, **kw)
        if request.session.uid in [None, False, ""]:
            pass
        else:
            request.env.user.email_verified = True
            _logger.info(f"    ==== user_id: {request.env.user} {request.env.user.name} email_verified: {request.env.user.email_verified}")
        return result