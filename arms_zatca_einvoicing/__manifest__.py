# -*- coding: utf-8 -*-
{
    'name': "ARMS E-Invoicing Module",

    'summary': """
        E-Invoicing with Simplified Invoice, VAT Invoice,
        Debit Note and Credit Note Invoice""",

    'description': """
        Long description of module's purpose
    """,

    'author': "ARMS-IT Company",
    'website': "http://www.armsit.com",


    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'ehcs_qr_code_base', 'account_debit_note'],

    # always loaded
    'data': [
        'data/payment_mean_data.xml',
        'security/ir.model.access.csv',
        'data/tax_codes_data.xml',
        'views/payment_mean_views.xml',
        'report/account_invoice_report_template.xml',
        'data/data.xml',
        'views/account_move_view.xml',
        'views/templates.xml',
        'views/res_company.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
