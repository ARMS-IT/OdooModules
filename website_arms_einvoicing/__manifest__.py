# -*- coding: utf-8 -*-
{
    'name': "Website Arms Einvoicing",
    'description': """
    """,
    'author': 'TraceNcode',
    'company': 'TraceNcode',
    'website': "https://tracencode.com",
    'category': 'point_of_sale',
    'version': '0.1',
    'depends': ['website', 'crm', 'website_form'],
    'data': [
        'views/assets.xml',
        'views/template.xml',
        'views/crm_lead.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
