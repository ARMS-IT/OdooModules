{
    'name': 'Recipe Management and Material Consumption',
    'version': '14.0.1',
    'category': 'Inventory',
    'summary': 'Recipe Material consumption',
    
    'author': 'TeamUp4Solutions, TaxDotCom',
    'website': 'http://taxdotcom.org/',
    'maintainer': 'Sohail Ahmad',
    
    'depends': ['base', 'uom','sale','sale_stock', 'stock', 'point_of_sale','report_xlsx'],#,'stock_account'
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/update_recipe_product_wizard.xml',
        'reports/report.xml',
        'views/stock_inventory.xml',
        'views/product.xml',
        'views/pos_order.xml',
        'views/sale_order.xml',
        'data/ir_sequence.xml',
        'data/stock_location.xml',
        'views/pos_assets.xml',
        'views/stock_move_line.xml',
    ],
    'installable': True,
    'auto_install': False,
    'price': 180.00,
    'currency': 'EUR',
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
}
