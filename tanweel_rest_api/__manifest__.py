# -*- coding: utf-8 -*-
{
    "name": "Rest API",
    "summary": """Restful API""",
    "version": "14.0.2.0.1",
    "category": "Extra Tools",
    "website": "https://erp.tracencode.com/",
    "author": "TraceNcode",
    "depends": ["base","account","sale_stock"],
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
    # "external_dependencies": {
    #     "python": [],
    #     "bin": [],
    # },
    "application": False,
    "installable": True,
    "auto_install": False,
    
}
