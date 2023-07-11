# -*- coding: utf-8 -*-

{
    'name': "Leave Request",
    'summary': """
        Employee request to leave""",
    'description': """

    """,

    'author': 'Radwan / Ahmad alsariera',
    'license': 'OPL-1',
    'website': '',
    'category': 'hr',
    'version': '14.0.1.0.8',
    'depends': ['hr','hr_holidays'],
    'data': [
#         'security/account_parent_security.xml',
        'security/ir.model.access.csv',
        'views/leave_request_views.xml',
#         'views/open_chart.xml',
#         'data/account_type_data.xml',
#         'views/account_parent_template.xml',
#         'views/report_coa_hierarchy.xml',
    ],
    'demo': [
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
}
