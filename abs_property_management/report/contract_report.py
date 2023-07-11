# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from odoo import api, models, fields
import datetime
import time

class ContractReport(models.AbstractModel):
    _name = 'report.abs_property_management.contract_report'
    _description = "Contract Report"

    contract_id = fields.Many2one('property.contract', string="Contracts")

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['property.contract'].browse(self.env.context.get('active_id'))
        contract_list = []
        contract_ids = self.env['property.contract'].search([('end_date','>=',docs.start_date),('end_date','<=',docs.end_date)])
        for contract_id in contract_ids:
            if contract_id:
                contract_list.append(contract_id)       
        docargs = {
                   'doc_ids'  : self.ids,
                   'docs'     : docs,
                   'time'     : time,
                   'contract_id': contract_list,
                  }
        if docargs:
            return docargs

