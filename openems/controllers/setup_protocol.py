import base64

from odoo import http
from odoo.http import request


class SetupProtocol(http.Controller):
    @http.route("/openems_backend/sendSetupProtocolEmail", type="json", auth="user")
    def index(self, setupProtocolId, edgeId):
        setupProtocolId = request.params["setupProtocolId"]
        edgeId = request.params["edgeId"]

        setup_protocol_model = request.env["openems.setup_protocol"]
        setup_protocol_record = setup_protocol_model.search_read(
            [("id", "=", setupProtocolId)]
        )
        if len(setup_protocol_record) != 1:
            raise ValueError("Setup protocol not found for id [" + edgeId + "]")

        device_model = request.env["openems.device"]
        device_rec = device_model.search_read([("name", "=", edgeId)])
        if len(device_rec) != 1:
            raise ValueError("Device not found for id [" + edgeId + "]")

        name = (
            "IBN-"
            + edgeId
            + "-"
            + setup_protocol_record[0]["create_date"].strftime("%d.%m.%Y")
            + ".pdf"
        )

        data = request.env.ref(
            "openems.action_openems_setup_protocol_report"
        )._render_qweb_pdf([setupProtocolId])
        attachment = request.env["ir.attachment"].create(
            {
                "res_model": "openems.device",
                "res_id": device_rec[0]["id"],
                "name": name,
                "store_fname": name,
                "datas": base64.b64encode(data[0]),
            }
        )

        email_values = {"attachment_ids": [attachment["id"]]}

        templateInstaller = request.env.ref("openems.setup_protocol_email_installer")
        templateInstaller.send_mail(
            setupProtocolId, email_values=email_values, force_send=True
        )
        templateCustomer = request.env.ref("openems.setup_protocol_email_customer")
        templateCustomer.send_mail(
            setupProtocolId, email_values=email_values, force_send=True
        )

        return {}
