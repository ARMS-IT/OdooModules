# -*- coding: utf-8 -*-
# from odoo import http


# class ZatcaReporting(http.Controller):
#     @http.route('/zatca_reporting/zatca_reporting/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/zatca_reporting/zatca_reporting/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('zatca_reporting.listing', {
#             'root': '/zatca_reporting/zatca_reporting',
#             'objects': http.request.env['zatca_reporting.zatca_reporting'].search([]),
#         })

#     @http.route('/zatca_reporting/zatca_reporting/objects/<model("zatca_reporting.zatca_reporting"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('zatca_reporting.object', {
#             'object': obj
#         })
