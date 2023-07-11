# -*- coding: utf-8 -*-
# from odoo import http


# class CustomPoReport(http.Controller):
#     @http.route('/custom_po_report/custom_po_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_po_report/custom_po_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_po_report.listing', {
#             'root': '/custom_po_report/custom_po_report',
#             'objects': http.request.env['custom_po_report.custom_po_report'].search([]),
#         })

#     @http.route('/custom_po_report/custom_po_report/objects/<model("custom_po_report.custom_po_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_po_report.object', {
#             'object': obj
#         })
