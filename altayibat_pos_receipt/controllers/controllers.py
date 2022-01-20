# -*- coding: utf-8 -*-
# from odoo import http


# class AltayibatPosReceipt(http.Controller):
#     @http.route('/altayibat_pos_receipt/altayibat_pos_receipt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/altayibat_pos_receipt/altayibat_pos_receipt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('altayibat_pos_receipt.listing', {
#             'root': '/altayibat_pos_receipt/altayibat_pos_receipt',
#             'objects': http.request.env['altayibat_pos_receipt.altayibat_pos_receipt'].search([]),
#         })

#     @http.route('/altayibat_pos_receipt/altayibat_pos_receipt/objects/<model("altayibat_pos_receipt.altayibat_pos_receipt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('altayibat_pos_receipt.object', {
#             'object': obj
#         })
