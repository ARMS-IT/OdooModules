# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class ConactForm(http.Controller):

    @http.route(['/contact-us'], type='http', auth="public", website=True)
    def contact_us(self, **post):
        request.env['crm.lead'].sudo().create({
                'name': post.get('company_name'),
                'partner_name': post.get('company_name'),
                'contact_name': post.get('name'),
                'email_from': post.get('email_from'),
                'phone': post.get('phone'),
                'city': post.get('city'),
                'description': post.get('description'),
                'industry': post.get('industry'),
                'organization_size': post.get('organization_size'),
                'subject': post.get('subject'),
            })
        return request.render("website_form.contactus_thanks", {})
