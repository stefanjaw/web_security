from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo import http
from odoo.http import request

import logging

_logger = logging.getLogger(__name__)


class AuthSignupHomeInherited(AuthSignupHome):

    @http.route(
        '/web/signup',
        type='http',
        auth='public',
        website=True,
        sitemap=False
    )
    def web_auth_signup(self, *args, **kw):
        _logger.info(
            "==== /web/signup web_auth_signup ============"
        )

        self._set_template_body_html_with_token()

        return super().web_auth_signup(*args, **kw)

    def _set_template_body_html_with_token(self):
        """
        Modifica la plantilla de creación de cuenta.

        Odoo 19:
            signup_type = 'signup' / 'reset'
            _generate_signup_token() = token real

        Esta función mantiene la lógica existente de modificar
        la plantilla directamente.
        """

        _logger.info(
            "==== _set_template_body_html_with_token"
        )

        template_id = request.env.ref(
            'auth_signup.mail_template_user_signup_account_created',
            raise_if_not_found=False
        )

        _logger.info(
            "Template auth_signup.mail_template_user_signup_account_created ",
            template_id
        )

        if not template_id:
            _logger.warning(
                "Template auth_signup.mail_template_user_signup_account_created "
                "not found"
            )
            return

        text_start = (
            '<div style="margin: 16px 0px 16px 0px;">'
        )

        text_end = 'Go to My Account'

        text_stop = '<!-- Modified Text -->'

        text_new = """
                    <div style="margin: 16px 0px 16px 0px;">
                        <!-- Modified Text -->
                    
                        <p style="margin:0px 0 16px 0;box-sizing:border-box;">
                            Click the button "Go to My account" or Copy and paste
                            the following URL into your browser:
                        </p>
                    
                        <t t-set="signup_token"
                           t-value="object.partner_id._generate_signup_token()"/>
                    
                        <pre style="margin:0px 0 16px 0;
                                    box-sizing:border-box;
                                    text-wrap-mode:wrap;
                                    white-space-collapse:preserve;
                                    color:#111827;
                                    overflow-y:auto;
                                    overflow-x:auto;
                                    unicode-bidi:bidi-override;
                                    direction:ltr;
                                    font-size:13px;
                                    background-color:#f4f4f4;
                                    padding:10px;
                                    border-radius:5px;
                                    font-family:monospace;"
                             t-out="'%sweb/login?auth_login=%s&amp;token=%s' % (
                                 request.httprequest.url_root,
                                 object.email,
                                 signup_token
                             )">
                        </pre>
                    
                        <a t-attf-href="/web/login?auth_login={{object.email}}&amp;token={{signup_token}}"
                           style="box-sizing:border-box;
                                  background-color:#875A7B;
                                  padding:8px 16px;
                                  text-decoration:none;
                                  color:#fff;
                                  border-radius:5px;
                                  font-size:13px;">
                            Go to My Account
                        </a>
                    </div>
                    """

        template_body_html = template_id.sudo().body_html
        template_body_html_str = str(template_body_html)

        start_index = template_body_html_str.find(
            text_start
        )

        end_index = template_body_html_str.find(
            text_end
        )

        stop_index = template_body_html_str.find(
            text_stop
        )

        if (
            start_index != -1
            and end_index != -1
            and stop_index == -1
        ):
            _logger.info(
                "==== Template Text Modified | %s: %s",
                template_id.id,
                template_id.name
            )

            end_index += len(text_end)

            template_body_html_str = (
                template_body_html_str[:start_index]
                + text_new
                + template_body_html_str[end_index:]
            )

            _logger.warning(
                "========== TEMPLATE BEFORE ==========\n%s\n======================================",
                template.sudo().body_html,
            )

            template_id.sudo().write({
                'body_html': template_body_html_str
            })

        return

    @http.route()
    def web_login(self, *args, **kw):
        """
        Intercepta el login para validar el token de signup.

        Odoo 19 utiliza tokens firmados. No se debe comparar
        directamente el token con signup_type.
        """

        _logger.info(
            "==== web_login check token"
        )

        redirect_if_logged_in = "/"

        try:
            result = self._validate_url_token(kw)

            if (
                result.get('redirect')
                and request.session.uid
                and request.session.uid > 4
            ):
                return request.redirect(
                    redirect_if_logged_in
                )

        except Exception:
            _logger.exception(
                "==== Error validating signup token"
            )

        return super().web_login(*args, **kw)

    def _validate_url_token(self, kw):
        """
        Valida el token firmado de Odoo 19.

        Odoo 19 utiliza:

            partner._generate_signup_token()

        para generar el token y:

            partner._signup_retrieve_partner(token)

        para validarlo.

        signup_type NO es el token.
        """

        token = kw.get('token')

        if not token:
            return {}

        _logger.info(
            "==== Validating signup token"
        )

        try:
            partner = request.env['res.partner'].sudo()._signup_retrieve_partner(
                token,
                check_validity=True,
                raise_exception=False,
            )

        except Exception:
            _logger.exception(
                "==== Error retrieving partner from signup token"
            )
            return {}

        if not partner:
            _logger.info(
                "==== Email Verification Failed: invalid token"
            )
            return {}

        user = partner.user_ids.filtered(
            lambda u: u.active
        )[:1]

        if not user:
            _logger.info(
                "==== Email Verification Failed: no active user"
            )
            return {}

        _logger.info(
            "==== web_login Email Verified | user=%s",
            user.login
        )

        user.sudo().write({
            'email_verified': True,
        })

        return {
            'redirect': True,
            'user_id': user.id,
        }

    @http.route(
        '/web/reset_password',
        type='http',
        auth='public',
        website=True,
        sitemap=False
    )
    def web_auth_reset_password(self, *args, **kw):
        """
        Mantiene el flujo estándar de Odoo 19 para reset de password.

        No marcamos email_verified simplemente porque existan
        token y login en la URL.
        """

        _logger.info(
            "==== web_auth_reset_password"
        )

        token = kw.get('token')
        login = kw.get('login')

        _logger.info(
            "==== reset password token=%s login=%s",
            bool(token),
            login
        )

        return super().web_auth_reset_password(
            *args,
            **kw
        )
