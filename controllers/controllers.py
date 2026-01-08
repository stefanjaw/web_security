# from odoo import http


# class WebSecurity(http.Controller):
#     @http.route('/web_security/web_security', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/web_security/web_security/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('web_security.listing', {
#             'root': '/web_security/web_security',
#             'objects': http.request.env['web_security.web_security'].search([]),
#         })

#     @http.route('/web_security/web_security/objects/<model("web_security.web_security"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('web_security.object', {
#             'object': obj
#         })

