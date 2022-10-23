# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class leaveRequest(models.Model):
	_name = "leave.request"
	_description = "Employee request leaves"
	
	employee_id = fields.Many2one('hr.employee',string='Employee Name')
	date = fields.Date('Date')
	request_type = fields.Selection([('personal', 'Personal Request'),
	                          ('work', 'Work Task')], 
	                          default='personal', string='Request Type')
	
	reason = fields.Text('Reason')
	empl_signature = fields.Binary(string='Employee Signature')
	
	dir_manager_id = fields.Many2one('hr.employee',string='Direct Manger')
	dir_manager_signature = fields.Binary(string='Manager Signature')
	from_time = fields.Float(string='From Time')
	to_time = fields.Float(string='To Time')
	request_time = fields.Float(string='Leave Time', readonly=True, compute='_compute_leave_time')
	state = fields.Selection(string='Status', copy=False, selection=[
            ('new', 'New'),
            ('1st_approve', 'HR Approval'),
            ('2nd_approve', 'Manager Approval'),
        ], default='new')
	
	@api.constrains('from_time', 'to_time')
	def _validate_time(self):
		for record in self:
			if record.to_time <= record.from_time:
				raise ValidationError(_("From time must be greater than To time."))
			if (record.to_time - record.from_time) < 2:
				raise ValidationError(_("Leave time requested must be at least 2 hours or half a day."))
	
	@api.depends('from_time','to_time')
	def _compute_leave_time(self):
		for rec in self:
			rec.request_time=rec.to_time - rec.from_time
			
	def button_first_approv(self):
		self.write({'state': '1st_approve'})
	
	def button_second_approv(self):
		self.write({'state': '2nd_approve'})
			
	
