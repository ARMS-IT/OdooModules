# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Invoice Sequence',
    'version': '14.0.4.7.0',
    'category': 'Uncategorized',
    'summary': 'This module update sequence prefix.',
    'sequence': '10',
    'author': 'ARMSIT',
    'license': 'LGPL-3',
    'company': 'ARMSIT',
    'maintainer': 'ARMSIT',
    'support': 'rayoub@armsit.com',
    'website': 'https://einvoicing.armsit.com/',
    'depends': ['account','zatca_e_invoicing'],
    'demo': [],
    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
    'qweb': [],
}
