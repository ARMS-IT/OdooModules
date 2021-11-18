# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'
    
    request_number = fields.Char("Req. Number")
    contract_number = fields.Char("Contract Number")
    
    po_approved_asked = fields.Boolean("PO Approved Asked", default= False)
    po_approved_asked_by_executice = fields.Boolean("PO Approved Asked By Executive", default= False)
    po_approved_asked_by_financier = fields.Boolean("PO Approved by Financial", default= False)

    po_executive_personal = fields.Many2one("res.users", string = "Executive Approved By", readonly= True, copy= False)
    po_financier_personal = fields.Many2one("res.users", string = "Financial Approved By", readonly= True, copy= False)
    date_executive_approval = fields.Datetime("Executive Approved Date", readonly=True, store=True)
    date_financier_approval = fields.Datetime("Financial Approved Date", readonly=True, store=True)
    state = fields.Selection(selection_add = [("approval_by_executive", "Executive Approval"),("approval_by_financier", "Financial Approval"),("approved", "Approved"),('purchase', 'Purchase Order')])
    revision_changes = fields.Char(string = "Revision")

    def button_ask_for_approval(self):
        self.po_approved_asked = True
        self.state = "approval_by_executive"

    def button_approval_by_executive(self):
        if self.user_has_groups("custom_purchase.management_user"):
            self.po_approved_asked_by_executice = True
            self.po_executive_personal = self._uid
            self.date_executive_approval = fields.Datetime.now()
            self.state = "approval_by_financier"
        return True
    
    def button_approval_by_financier(self):
        if self.user_has_groups("custom_purchase.finance_user"):
            if self.po_approved_asked_by_executice == True:
                self.po_approved_asked_by_financier = True
                self.po_financier_personal = self.env.user.id
                self.date_financier_approval = fields.Datetime.now()
                self.state = "approved"
        return True 

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'approved']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def get_pol_seq_num(self):
        count = 0
        for line in self.order_id.order_line:
            count += 1
            line.new_seq_num = str(format(count, "03d"))

    new_seq_num	= fields.Char(string = "S No.", compute=get_pol_seq_num)
