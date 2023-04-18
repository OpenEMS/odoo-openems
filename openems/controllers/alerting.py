import logging
from datetime import  datetime

from odoo import http
from odoo.http import request

class Message:
    sentAt: datetime
    edgeId: str
    userIds: list[int]

    def __init__(self, sentAt: datetime, edgeId: str, userIds: list[int]) -> None:
        self.sentAt = sentAt
        self.edgeId = edgeId
        self.userIds = userIds

class Alerting(http.Controller):
    __logger = logging.getLogger("Alerting")

    @http.route("/openems_backend/send_alerting_email", type="json", auth="user")
    def old(self, ids: list, now: str, edgeId: str = ''):
        params = [{"edgeId":edgeId, "recipients":ids}]
        self.index(now, params)

    @http.route("/openems_backend/mail/alerting_email", type="json", auth="user")
    def index(self, sentAt: str, params: list[dict]):
        msgs = self.__get_params(sentAt, params)

        for msg in msgs:
            template = self.__get_template(msg.edgeId)
            self.__send_mails(template, msg)

        return {}

    def __get_params(self, sentAt, params) -> list[Message]:
        msgs = list()
        sent = datetime.strptime(sentAt, "%Y-%m-%d %H:%M:%S")
        for param in params:
            msgs.append(Message(sent, param["edgeId"], param["recipients"]));
        return msgs

    def __get_template(self, device_id):
        template = request.env.ref("openems.alerting_email_generic")
        return template

    def __send_mails(self, template, msg: Message):
        roles = http.request.env["openems.device_user_role"].search([("id","in",msg.userIds),("device_id","=",msg.edgeId)])
        for role in roles:
            try:
                template.send_mail(res_id=role.id, force_send=True)
                role.write({"last_notification": msg.sentAt})
            except Exception as err:
                self.__logger.error("[" + str(err) + "] Unable to send template[" + str(template.name) +"] to edgeUser[user=" + str(role.id) + ", edge=" + str(msg.edgeId)+ "]")