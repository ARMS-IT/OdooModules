# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Balikh Report Layout',
    'version': '14.0.3.7.0',
    'category': 'Uncategorized',
    'summary': 'This module adds a new custom layout for the reports.',
    'sequence': '10',
    'author': 'ARMSIT',
    'license': 'LGPL-3',
    'company': 'ARMSIT',
    'maintainer': 'ARMSIT',
    'support': 'rayoub@armsit.com',
    'website': 'https://einvoicing.armsit.com/',
    'depends': ['web'],
    'demo': [],
    'data': [
        'views/report_layout.xml',
        'data/data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': [],
    'qweb': [],
}
