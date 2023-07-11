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
{
    'name'    : "Property Management",
    'author'  : 'Ascetic Business Solution',
    'category': 'Sales',
    'summary' : "Manage your property for selling and rent.",
    'website' : 'http://www.asceticbs.com',
    'description': """ """,
    'version' : '14.0.1.0',
    'depends' : ['base','sale_management','attachment_indexation'],
    'data'    : ['security/property_security.xml',
                 'security/ir.model.access.csv',
                 "wizard/installment_detail_wizard_view.xml",
                 "wizard/contract_detail_wizard_view.xml",
                 "wizard/contract_report_wizard_view.xml",
                 "views/product_template_view.xml",
                 "views/property_and_tenant_history_view.xml",
                 "views/property_configuration.xml",
                 "views/res_partner_view.xml",
                 "views/property_contract_view.xml",
                 "views/contract_renewal_date_schedular_view.xml",
                 "views/property_maintenance.xml",
                 "views/contract_expiry_report.xml",
                 "views/contract_report_action.xml",
                 "views/contract_report_template.xml",
                 "views/contract_type.xml",
                 "views/property_installment_view.xml",
                 "report/account_invoice_report.xml"
                ],
    'license': 'OPL-1',
    'live_test_url' : "http://www.test.asceticbs.com/web/database/selector",
    'price': 120.00, 
    'currency': "EUR",
    'images': ['static/description/banner.png'],
    'installable' : True,
    'application' : True,
    'auto_install': False,
}

