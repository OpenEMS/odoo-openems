import logging
from datetime import  datetime
from enum import Enum

from odoo import http
from odoo.http import request

class SumState(Enum):
    FAULT = 0 
    WARNING = 1

class Message:
    sentAt: datetime
    edgeId: str
    userLogins: list[str]

    def __init__(self, sentAt: datetime, edgeId: str, userLogins : list[str]) -> None:
        self.sentAt = sentAt
        self.edgeId = edgeId
        self.userLogins = userLogins 
        
class SumStateMessage(Message):
    state: SumState
    
    def __init__(self, sentAt: datetime, edgeId: str, userLogins: list[str], state: SumState) -> None:
        super().__init__(sentAt, edgeId, userLogins)
        self.state = state

class Alerting(http.Controller):
    __logger = logging.getLogger("Alerting")
    __datetime_format = "%Y-%m-%d %H:%M:%S"

    @http.route("/openems_backend/mail/alerting_sum_state", type="json", auth="user")
    def sum_state_alerting(self, sentAt: str, params: list[dict]) -> dict:
        msgs = self.__get_sum_state_params(sentAt, params)
        update_func = lambda role, at: { role.write({"sum_state_last_notification": at})}
        
        if len(msgs) == 0:
            self.__logger.error("Scheduled SumState-Alerting-Mail without any recipients!!!")
            return {"status": "error", "message": "No recipients for sum state alerting"}
        
        template = request.env.ref('openems.alerting_sum_state')
        mails_sent = 0
        for msg in msgs:
            mails_sent += self.__send_mails(template, msg, update_func)
                  
        return {"status": "success", "mails_sent": mails_sent}

    @http.route("/openems_backend/mail/alerting_offline", type="json", auth="user")
    def offline_alerting(self, sentAt: str, params: list[dict]) -> dict:
        msgs = self.__get_offline_params(sentAt, params)
        update_func = lambda role, at: { role.write({"offline_last_notification": at})}

        if len(msgs) == 0:
            self.__logger.error("Scheduled Offline-Alerting-Mail without any recipients!!!")
            return {"status": "error", "message": "No recipients for offline alerting"}
			
        mails_sent = 0

        for msg in msgs:
            template = self.__get_template(msg.edgeId)
            mails_sent += self.__send_mails(template, msg, update_func)

        return {"status": "success", "mails_sent": mails_sent}

    def __get_offline_params(self, sentAt, params) -> list[Message]:
        msgs = list()
        sent = datetime.strptime(sentAt, self.__datetime_format)
        for param in params:
            edgeId = param["edgeId"]
            recipients = param["recipients"]
            msgs.append(Message(sent, edgeId, recipients));
        return msgs
    
    def __get_sum_state_params(self, sentAt, params) -> list[SumStateMessage]:
        msgs = list()
        sent = datetime.strptime(sentAt, self.__datetime_format)
        for param in params:
            edgeId = param["edgeId"]
            recipients = param["recipients"]
            state = param["state"]
            msgs.append(SumStateMessage(sent, edgeId, recipients, state));
        return msgs
    
    def __get_template(self, device_id):
        oem, producttype = self.__get_device_data_for(device_id)
        match (oem.casefold(), producttype.casefold()):
            case ('openems', _):
                return request.env.ref("openems.alerting_offline")

    def __get_device_data_for(self, device_id) -> tuple[str, str]:
        if device_id:
            found_devices = http.request.env["openems.device"].search_read(
                [("name", "=", device_id)], ["producttype", "oem"]
            )
            if len(found_devices) == 1:
                device = found_devices[0]
                oem = device.get('oem') or 'openems'
                producttype = device.get('producttype') or 'other'
                return oem, producttype

            self.__logger.warning(f"no device with id '{device_id}' found, using fallback [oem=openems, producttype=other]")
        return 'openems', 'other'
               
    def __send_mails(self, template, msg: Message, update_func) -> int:
        roles = http.request.env['openems.alerting'].search(
            [('user_login','in', msg.userLogins),('device_id','=', msg.edgeId)]
        )
        
        if not roles or len(roles) == 0:
            self.__logger.error(f"No AlertingSettings found for edgeId[{msg.edgeId}] and userLogins[{msg.userLogins}]!!!")
            return 0
        
        mails_sent = 0
        for role in roles:
            try:
                template.send_mail(res_id=role.id)
                update_func(role, msg.sentAt)
                mails_sent += 1
            except Exception as err:
                self.__logger.error(f"[{err}] Unable to send template[{template.name}] to edgeUser[user={role.id}, edge={msg.edgeId}]")
        return mails_sent