{
    'name': 'Equipment Loan',
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Track equipment loans to contacts',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/equipment_item_views.xml',
        'views/equipment_loan_views.xml',
        'views/menus.xml',
    ],
    'application': True,
    'installable': True,
}