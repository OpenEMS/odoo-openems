{
    "name": "OpenEMS",
    "summary": "Everything related to OpenEMS (Open Energy Management System)",
    "version": "14.0.1.0.0",
    "author": "OpenEMS Association e.V.",
    "maintainer": "OpenEMS Association e.V.",
    "contributors": [
        "Stefan Feilmeier <stefan.feilmeier@fenecon.de>"
        "Maximilian Lang <maximilian.lang@fenecon.de>"
    ],
    "website": "https://openems.io",
    "license": "AGPL-3",
    "category": "Specific Industry Applications",
    "depends": ["base", "web", "mail", "crm", "resource", "stock", "web_m2x_options"],
    "data": [
        "security/openems.xml",
        "security/ir.model.access.csv",
        "views/device.xml",
        "views/partner.xml",
        "views/setup_protocol.xml",
        "views/user.xml",
        "report/setup_protocol.xml",
        "mail/setup_protocol.xml",
        "mail/alerting.xml",
        "mail/user.xml",
        "data/ir_config_parameter.xml",
        "data/res_partner_category.xml",
    ],
    "demo": ["data/demo.xml"],
    "js": [],
    "css": [],
    "qweb": [],
    "images": [],
    "test": [],
    "installable": True,
}
