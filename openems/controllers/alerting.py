from datetime import datetime, timezone
from odoo import http
from odoo.http import request

import logging

_logger = logging.getLogger("Alerting")


class Alerting_Owner(http.Controller):

    @http.route('/openems_backend/send_alerting_email', type='json', auth='user')
    def index(self, ids, now):
        ids = request.params['ids']
        _logger.debug("queue notification mails to " + str(len(ids)) + " users")

        now_string = request.params['now']
        now = datetime.strptime(now_string, '%Y-%m-%d %H:%M:%S.%f')

        notify_role = http.request.env['openems.device_user_role']
        template = request.env.ref("openems.alerting_email_notify")

        force_send = len(ids) <= 10

        for id in ids:
            exists = notify_role.browse(id)
            if exists:
                template.send_mail(res_id=id, force_send=force_send)
                exists.write({'last_notification': now})

        return {}
