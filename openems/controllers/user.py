from odoo import http
from odoo.http import request
import base64

class User(http.Controller):

    @http.route('/openems_backend/sendRegistrationEmail', type='json', auth='user')
    def index(self, userId, password=None):
        user_model = request.env['res.users']
        user_record = user_model.search_read([('id', '=', userId)], ['partner_id'])
        if len(user_record) != 1:
            raise ValueError('User not found for id [' + userId + ']')

        partner = user_record[0]
        partner_id = partner.get('partner_id')
        if partner_id is None: 
            raise ValueError('User has no partner')

        partner_model = request.env['res.partner']
        partner_record = partner_model.search_read([('id', '=', partner_id[0])], ['firstname', 'lastname', 'email'])

        id = partner_record[0].get('id')
        name = partner_record[0].get('firstname') + ' ' + partner_record[0].get('lastname')
        email = partner_record[0].get('email')

        if password is None:
            password = '*****'

        body = """
            <p>Your account for OpenEMS Backend has been created.</p>
            <p>
                E-Mail: {email}<br>
                Passwort: {password}<br>
            </p>
        """.format(name=name, email=email, password=password)

        email_values = {
            "body_html": body
        }

        templateRegistration = request.env.ref("openems.registration_email")
        templateRegistration.send_mail(res_id=id, email_values=email_values, force_send=True)

        return {}