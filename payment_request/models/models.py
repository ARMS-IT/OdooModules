# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PaymentRequest(models.Model):
    _name = 'payment.request.new'
    _description = 'Payment Request New'
    _rec_name = 'customer'

    date = fields.Date("Date")
    current_user = fields.Many2one('res.users', 'Requester Name', default=lambda self: self.env.user)
    payment_method = fields.Selection([
        ('bank_transfer', 'Bank Transfer'),
        ('cash_payment', 'Cash Payment'),
        ('sadad_payment', 'Sadad Payment'),
        ('tba', 'Transfer Between Accounts (TBA)'),
    ], string="Payment Method")
    tba = fields.Char(string="TBA #")
    payment_type = fields.Many2one('account.account', string="Payment Type")
    amount_requested = fields.Integer(string="Amount Requested")
    bank_number = fields.Many2one('account.journal', string="Bank Number")
    project_name = fields.Many2one('project.project', 'Project Name')
    customer = fields.Many2one('res.partner', "Customer")
    qnet_account = fields.Char("QNET Bank Account Number")
    beneficiary_name = fields.Char("Beneficiary name")
    project_wo = fields.Char("Project WO")
    approved_by = fields.Many2one('hr.employee', "Approved By")
    currency = fields.Many2one('res.currency', "Currency")
    department = fields.Many2one('hr.department', "Department", domain=[('name', 'ilike', 'Finance')])
    payment_purpose = fields.Text('payment Purpose')