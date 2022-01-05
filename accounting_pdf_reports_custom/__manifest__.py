# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 14 Accounting PDF Reports Custom',
    'version': '14.0.3.7.0',
    'category': 'Invoicing Management',
    'summary': 'Accounting Reports For Odoo customisation',
    'sequence': '10',
    'author': 'ARMSIT',
    'license': 'LGPL-3',
    'company': 'ARMSIT',
    'maintainer': 'ARMSIT',
    'support': 'rayoub@armsit.com',
    'website': 'https://einvoicing.armsit.com/',
    'depends': ['account','accounting_pdf_reports'],
    'demo': [],
    'data': [
        'views/report_layout.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
    'qweb': [],
}
