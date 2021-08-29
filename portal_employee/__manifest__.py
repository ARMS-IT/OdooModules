# -*- coding: utf-8 -*-

{
    'name': 'Portal Employee',
    'version': '14.0',
    'summary': 'Portal Employee',
    'description': 'This module will help to portal employee for managing leave, payslip etc.',
    'author': 'TraceNcode',
    'company': 'TraceNcode',
    'website': "https://tracencode.com",
    'depends': ['portal', 'website', 'hr_payroll_community'],
    'data': [
        'views/assets.xml',
        'views/template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
