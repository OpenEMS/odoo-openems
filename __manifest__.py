{
    'name': 'OpenEMS',
    'summary': 'Everything related to OpenEMS (Open Energy Management System)',
    'description': "Everything related to OpenEMS (Open Energy Management System)",
    'version': '1.0.0',

    'author': 'OpenEMS Association e.V.',
    'maintainer': 'OpenEMS Association e.V.',
    'contributors': ['Stefan Feilmeier <stefan.feilmeier@fenecon.de>'],

    'website': 'https://openems.io',

    'license': 'AGPL-3',
    'category': 'Specific Industry Applications',

    'depends': [
        'base', 'web', 'mail', 'crm', 'resource', 'web_m2x_options'
    ],
    'data': [
        'security/edge.xml',
        'security/ir.model.access.csv',
        'views/setup_protocol.xml',
        'views/user.xml',
        'views/edge.xml',
        'report/setup_protocol.xml',
        'mail/setup_protocol.xml',
        'mail/user.xml',
        'data/ir_config_parameter.xml'
    ],
    'demo': [
    ],
    'js': [
    ],
    'css': [
    ],
    'qweb': [
    ],
    'images': [
    ],
    'test': [
    ],

    'installable': True
}
