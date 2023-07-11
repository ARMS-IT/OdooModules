# -*- coding: utf-8 -*-
{
    'name': "joman_pos_receipt",
    'summary': """ POS logo and adress for multi shopes""",
    'description': """Long description of module's purpose""",
    'author': "ARMSIT",
    'website': "http://www.armsit.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    'qweb': [

        'static/src/xml/Screens/ReceiptScreen/OrderReceipt.xml',
   	'static/src/xml/Screens/ReceiptScreen/pos_ticket_view.xml',
    	'static/src/xml/Screens/ReceiptScreen/pos_screen_image_view.xml'

    ],
}
