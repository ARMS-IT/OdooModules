# -*- coding: utf-8 -*-
{
    "name": "Automatic Vendor Number",
    "version": "1.0.2",
    'license': 'LGPL-3',
    'author': 'Josef Kaser, pragmasoft',
    'website': 'https://www.pragmasoft.de',
    "summary": """
    Automatically create the vendor number from a sequence when a vendor is being created.
    """,
    "description": """
Automatic Vendor Number
=========================
Automatically create the vendor number from a sequence when a vendor is being created.

The vendor number can be configured in the sequence "Vendor Number".
    """,
    "category": "Purchase",
    "depends": [
        "base",
        "purchase",
    ],
    "data": [
        "data/sequencer.xml"
    ],
    "installable": True,
    "auto_install": False,
}
