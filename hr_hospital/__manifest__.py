{
    'name': 'Hospital',
    'summary': 'Hospital HR',
    'author': 'Denys Vialov',
    'website': 'https://github.com/DenysV76/odoo-course',
    'category': 'Customizations',
    'license': 'LGPL-3',
    'version': '19.0.1.0.0',

    'depends': [
        'base',
    ],

    'external_dependencies': {
        'python': [],
    },

    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
}
