# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class EmployeeLetterRequest(models.Model):
    _name = 'employee.letter.request'
    _description = 'Employee Letter Request'
    _order = 'name'

    name = fields.Char(string='Name', help="Name")
    employee_id = fields.Many2one("hr.employee","Employee",required=True)
    ltype = fields.Selection(selection=[
        ('arabic', 'Arabic'),
        ('english', 'English'),
    ], string="Language", default="arabic", required=True)
    # sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)
    position = fields.Selection(selection=[
        ('iqama_position', 'Iqama Position'),
        ('company_position', 'Company Position'),
    ], string="Position", default="iqama_position", required=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    ], string="Status", default="draft", required=True)
    salary = fields.Boolean("Salary")
    chamber_of_commerce = fields.Boolean("Chamber of Commerce")
    description = fields.Text(string='Description',required=True)
    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')

    def _check_approval_update(self):
        """ Check if target state is achievable. """
        if self.env.is_superuser():
            return

        # current_employee = self.env.user.employee_id
        is_officer = self.env.user.has_group('hr.group_hr_user')

        for letter in self:
            if not is_officer or self.env.user != letter.employee_id.parent_id.user_id:
                    raise UserError(_('You must be either %s\'s Manager to approve this request') % (letter.employee_id.name))
            letter.check_access_rule('write')

    @api.depends('state', 'employee_id')
    def _compute_can_approve(self):
        for letter in self:
            try:
                if letter.state == 'draft':
                    letter._check_approval_update()
            except (AccessError, UserError):
                letter.can_approve = False
            else:
                letter.can_approve = True

    @api.model
    def create(self, vals):
        res = super(EmployeeLetterRequest, self).create(vals)
        res['name'] = self.env['ir.sequence'].next_by_code('employee.letter.request.sequence')
        return res

    def action_approve(self):
        self.state = 'approved'

    def action_refuse(self):
        self.state = 'refused'
