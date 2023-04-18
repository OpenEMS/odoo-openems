from odoo.modules.module import get_module_resource

import base64

OPENEMS_LOGO_BASE64 = base64.b64encode(open(get_module_resource('openems', 'mail/openems/', 'OpenEMS-Logo.jpg') , "rb").read())