# -*- coding: utf-8 -*-
{
    'name': "POS Receipt Customization",
    'description': """
        This module is regarding pos customization.
    """,
    'author': 'TraceNcode',
    'company': 'TraceNcode',
    'website': "https://tracencode.com",
    'category': 'point_of_sale',
    'version': '0.1',
    'depends': ['point_of_sale'],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/Screens/ReceiptScreen/OrderReceipt.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
