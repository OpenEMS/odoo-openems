from odoo import http
from odoo.http import request
import base64

class SetupProtocol(http.Controller):

    @http.route('/openems_backend/sendSetupProtocolEmail', type='json', auth='user')
    def index(self, setupProtocolId, edgeId):
        setupProtocolId = request.params['setupProtocolId']
        edgeId = request.params['edgeId']

        setup_protocol_model = request.env['openems.setup_protocol']
        setup_protocol_record = setup_protocol_model.search_read([('id', '=', setupProtocolId)])
        if len(setup_protocol_record) != 1:
            raise ValueError('Setup protocol not found for id [' + edgeId + ']')

        openems_edge_model = request.env['openems.edge']
        openems_edge_record = openems_edge_model.search_read([('name', '=', edgeId)])
        if len(openems_edge_record) != 1:
            raise ValueError('OpenEMS Edge not found for id [' + edgeId + ']')

        name = 'IBN-' + edgeId + "-" + setup_protocol_record[0]['create_date'].strftime('%d.%m.%Y') + ".pdf"

        data = request.env.ref('openems.action_openems_setup_protocol_report').render([setupProtocolId])
        attachment = request.env['ir.attachment'].create({
            'res_model': 'openems.edge',
            'res_id': openems_edge_record[0]['id'],
            'name': name,
            'datas_fname': name,
            'datas': base64.encodestring(data[0]),
        })

        email_values = {
            "attachment_ids": [attachment['id']]
        }

        templateInstaller = request.env.ref("openems.setup_protocol_email_installer")
        templateInstaller.send_mail(setupProtocolId, email_values=email_values, force_send=True)
        templateCustomer = request.env.ref("openems.setup_protocol_email_customer")
        templateCustomer.send_mail(setupProtocolId, email_values=email_values, force_send=True)

        return {}