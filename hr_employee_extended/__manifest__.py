{
    # Product Info
    'name': 'HR Extended',
    'version': '14.0.0.1',
    'license': 'OPL-1',
    'category': 'Human Resources/Time Off',
    'summary': 'HR Extended Module helps you to extended the features of Base HR Moudle',
    
    
    # Dependencies
    'depends': ['base_setup', 'hr'],
    
    # View
    'data': ['data/hr_employee_new_seq.xml',
             'views/hr_employee_views.xml',
             'views/hr_employee_public_views.xml'],
    
    # Technical 
    'installable': True,
    'auto_install': False,
    'application': True}
