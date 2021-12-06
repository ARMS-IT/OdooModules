# -*- coding: utf-8 -*-
# from odoo import http


# class InvoiceAnalyticReadonly(http.Controller):
#     @http.route('/invoice_analytic_readonly/invoice_analytic_readonly/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_analytic_readonly/invoice_analytic_readonly/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_analytic_readonly.listing', {
#             'root': '/invoice_analytic_readonly/invoice_analytic_readonly',
#             'objects': http.request.env['invoice_analytic_readonly.invoice_analytic_readonly'].search([]),
#         })

#     @http.route('/invoice_analytic_readonly/invoice_analytic_readonly/objects/<model("invoice_analytic_readonly.invoice_analytic_readonly"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_analytic_readonly.object', {
#             'object': obj
#         })
