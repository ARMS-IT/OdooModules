# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Order Types for POS',
    'version': '14.0.0.0',
    'category': 'Point of Sale',
    'summary': 'Order type for point of sale order type on pos order type for pos different order type on pos type of order on pos order types for point of sale types of order pos home delivery pos parcel type pos take away pos delivery order pos order parcel on pos order',
    'description' :"""

            POS Order Types in odoo,
            Type of POS Order in odoo,
            Create Type of POS Order in odoo,
            Enable/Disable Type of POS Order in odoo,
            Select Type of POS Order in odoo,
            Type of POS Order Displayed in Receipt in odoo,
            Type of POS Order Displayed in Backend POS Order in odoo, 

    """,
    'author': 'BrowseInfo',
    "price": 9,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'depends': ['base','point_of_sale'],
    'qweb': [
        'static/src/xml/pos_order_type.xml',
        'static/src/xml/OrderTypePopup.xml',

    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_assets.xml',
        'views/pos_config_inherit.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/fHogptygkO4',
    "images":['static/description/Banner.png'],
}
