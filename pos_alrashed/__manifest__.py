# -*- coding: utf-8 -*-
{
    "name": "API To generate invoice in odoo.",
    "summary": """API To generate invoice in odoo""",
    "version": "14.0.2.0.1",
    "category": "Extra Tools",
    "website": "https://armsit.com/",
    "author": "ARMSIT",
    "depends": ["base","account","sale_stock",'point_of_sale'],
    "data": [
        "security/ir.model.access.csv",
        "views/rest_menu.xml",
        "views/rest_token_view.xml",
        "views/views.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "images": [
        'static/description/banner.png'
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    
}
