# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.point_of_sale.controllers.main import PosController
from odoo import http
from odoo.http import request

from odoo.osv.expression import AND



class POSPosControllerInherit(PosController):

    @http.route(['/pos/web', '/pos/ui'], type='http', auth='user')
    def pos_web(self, config_id=False, **k):
        domain = [
                ('state', 'in', ['opening_control', 'opened']),
                ('user_id', '=', request.session.uid),
                ('rescue', '=', False)
                ]
        if config_id:
            domain = AND([domain,[('config_id', '=', int(config_id))]])
        pos_session = request.env['pos.session'].sudo().search(domain, limit=1)
        company = pos_session.company_id

        response = super(POSPosControllerInherit, self).pos_web(config_id=config_id, **k)
        response.qcontext['session_info']['user_companies'] = {'current_company': (company.id, company.name),
                                                               'allowed_companies': [(company.id, company.name)],
                                                               'allowed_branches': [(company.id,{ 'name':company.name,'street':company.street,'street2':company.street2,'city':company.city,'vat':company.vat,'country':company.country_id.name}) for company in request.env.user.company_ids]}
        return response

