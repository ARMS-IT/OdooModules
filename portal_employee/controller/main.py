# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError
import base64
from io import BytesIO
from base64 import b64decode
from datetime import datetime


class CustomerPortal(CustomerPortal):

    @http.route(['/employee/profile/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def employee_profile_update(self, **kw):
        value = {}
        gender = False
        marital_status = False
        if kw.get('gender') == 'Male':
            gender = 'male'
        if kw.get('gender') == 'Female':
            gender = 'female'
        if kw.get('gender') == 'Other':
            gender = 'other'
        if kw.get('marital_status') == 'Single':
            marital_status = 'single'
        if kw.get('marital_status') == 'Married':
            marital_status = 'married'
        current_login_user = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', current_login_user.id)], limit=1)
        country_id = request.env['res.country'].sudo().search([('id', '=', int(kw.get('private_country_id')))], limit=1)
        state_id = request.env['res.country.state'].sudo().search([('id', '=', int(kw.get('private_state_id')))], limit=1)
        if kw.get('image'):
            image = BytesIO(b64decode(kw.get('image').split(',')[1]))
            employee_id.update({'image_1920': base64.b64encode(image.read()).decode('utf-8')})
        employee_id.update({
                'name': kw.get('name'),
                'identification_id': kw.get('identification_id'),
                'passport_id': kw.get('passport_id'),
                'birthday': kw.get('birthday'),
                'gender': gender,
                'marital': marital_status,
            })
        employee_id.address_home_id.update({
                'street': kw.get('private_street'),
                'street2': kw.get('private_street2'),
                'zip': kw.get('private_zip'),
                'state_id': state_id.id,
                'country_id': country_id.id,
            })
        value['render_employee_data'] = request.env['ir.ui.view']._render_template("portal_employee.portal_employee_data", {
            })
        value['render_employee_form'] = request.env['ir.ui.view']._render_template("portal_employee.portal_employee_form", {
            })
        return value

    @http.route(['/manager/employee/profile/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def manager_employee_profile_update(self, **kw):
        value = {}
        employee_id = request.env['hr.employee'].sudo().browse(int(kw.get('employee_id')))
        value['render_employee_form'] = request.env['ir.ui.view']._render_template("portal_employee.manager_portal_employee_form", {'employee_id': employee_id})
        return value

    @http.route(['/save/employee/profile/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def save_employee_profile_update(self, **kw):
        value = {}
        gender = False
        marital_status = False
        if kw.get('gender') == 'Male':
            gender = 'male'
        if kw.get('gender') == 'Female':
            gender = 'female'
        if kw.get('gender') == 'Other':
            gender = 'other'
        if kw.get('marital_status') == 'Single':
            marital_status = 'single'
        if kw.get('marital_status') == 'Married':
            marital_status = 'married'
        employee_id = request.env['hr.employee'].sudo().search([('id', '=', int(kw.get('emp_id')))], limit=1)
        country_id = request.env['res.country'].sudo().search([('id', '=', int(kw.get('private_country_id')))], limit=1)
        state_id = request.env['res.country.state'].sudo().search([('id', '=', int(kw.get('private_state_id')))], limit=1)
        if kw.get('image'):
            image = BytesIO(b64decode(kw.get('image').split(',')[1]))
            employee_id.update({'image_1920': base64.b64encode(image.read()).decode('utf-8')})
        employee_id.update({
                'name': kw.get('name'),
                'identification_id': kw.get('identification_id'),
                'passport_id': kw.get('passport_id'),
                'birthday': kw.get('birthday'),
                'gender': gender,
                'marital': marital_status,
            })
        employee_id.address_home_id.update({
                'street': kw.get('private_street'),
                'street2': kw.get('private_street2'),
                'zip': kw.get('private_zip'),
                'state_id': state_id.id,
                'country_id': country_id.id,
            })
        value['render_o_organizational_chart'] = request.env['ir.ui.view']._render_template("portal_employee.o_organizational_chart", {})
        return value

    @http.route(['/leave/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def leave_update_json(self, **kw):
        value = {}
        current_login_user = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', current_login_user.id)], limit=1)
        holiday = request.env['hr.leave'].sudo()
        holiday.create({
                'employee_id': employee_id.id,
                'request_date_from': kw.get('from_date'),
                'request_date_to': kw.get('to_date'),
                'name': kw.get('description'),
                'holiday_status_id': int(kw.get('holiday_status_id')),
                'number_of_days': int(kw.get('number_of_days'))
            })
        value['leave_data'] = request.env['ir.ui.view']._render_template("portal_employee.leave_data", {
            })
        value['render_leave_form'] = request.env['ir.ui.view']._render_template("portal_employee.leave_form", {
            })
        return value

    @http.route(['/calculate/number_of_days'], type='json', auth="public", methods=['POST'], website=True)
    def calculate_number_of_days(self, **kw):
        current_login_user = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', current_login_user.id)], limit=1)
        holiday = request.env['hr.leave'].sudo().search([('employee_id', '=', employee_id.id)], limit=1)
        if kw.get('from_date') and kw.get('to_date'):
            from_date = datetime.strptime(kw.get('from_date'), '%Y-%m-%d')
            to_date = datetime.strptime(kw.get('to_date'), '%Y-%m-%d')
            days = holiday._get_number_of_days(from_date, to_date, holiday.employee_id.id)['days']
            return days+1

    @http.route(['/my/payslip/report/<int:payslip_id>'], type='http', auth="public", website=True)
    def print_payslip(self, payslip_id, access_token=None, report_type=None, download=False, **kw):
        current_login_user = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', current_login_user.id)], limit=1)
        payslip = request.env['hr.payslip'].sudo().browse(int(payslip_id))
        if employee_id.id == payslip.employee_id.id:
            try:
                payslip = self._document_check_access('hr.payslip', payslip_id)
            except (AccessError, MissingError):
                return request.redirect('/my')
            if report_type in ('html', 'pdf', 'text'):
                return self._show_report(model=payslip, report_type=report_type, report_ref='hr_payroll_community.action_report_payslip', download=download)

    @http.route(['/approve/leave_update_json'], type='json', auth="public", methods=['POST'], website=True)
    def approve_leave(self, **kw):
        value = {}
        leave_id = request.env['hr.leave'].sudo().browse(int(kw.get('leave_id')))
        leave_id.action_approve()
        value['leave_data'] = request.env['ir.ui.view']._render_template("portal_employee.leave_data", {
            })
        return value

    @http.route(['/refuse/leave_update_json'], type='json', auth="public", methods=['POST'], website=True)
    def refuse_leave(self, **kw):
        value = {}
        leave_id = request.env['hr.leave'].sudo().browse(int(kw.get('leave_id')))
        leave_id.action_refuse()
        value['leave_data'] = request.env['ir.ui.view']._render_template("portal_employee.leave_data", {
            })
        return value
