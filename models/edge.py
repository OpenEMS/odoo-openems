from datetime import datetime
from odoo import models, fields, api, _

class Edge(models.Model):
    _name = 'openems.edge'
    _description = "OpenEMS Edge"
    _inherit = 'mail.thread'
    _order = "name_number asc"
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Name needs to be unique')
    ]

    name = fields.Char(required=True)
    active = fields.Boolean('Active', default=True, track_visibility='onchange')
    comment = fields.Char(track_visibility='onchange')
    internalnote = fields.Text('Internal note', track_visibility='onchange')

    monitoring_url = fields.Char('Online-Monitoring', compute="_compute_monitoring_url", store=False)

    @api.depends("name")
    def _compute_monitoring_url(self):
        for rec in self:
            if rec.name:
                url = self.env['ir.config_parameter'].sudo().get_param('edge.monitoring.url')
                rec.monitoring_url = url + rec.name

    # Settings
    openems_config = fields.Text('OpenEMS Config Full')
    openems_config_components = fields.Text('OpenEMS Config')
    openems_version = fields.Char('OpenEMS Version', track_visibility='onchange')

    # Security
    setup_password = fields.Char(u'Installateursschlüssel (Installation key)', help='Passwort für die Inbetriebnahme durch den Installateur')
    apikey = fields.Char('API-Key', required=True, track_visibility='onchange')

    # 'openems_sum_state_level' is updated by OpenEMS Backend 
    openems_sum_state_level = fields.Selection([
        ('ok', 'Ok'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('fault', 'Fault')
    ], 'OpenEMS State')
    # 'openems_is_connected' is updated by OpenEMS Backend 
    openems_is_connected = fields.Boolean('OpenEMS Is connected')

    # System Status
    lastmessage = fields.Datetime("Last message")
    lastupdate = fields.Datetime("Last data update")

    # Verknüpfungen
    user_role_ids = fields.One2many("openems.edge_user_role", "edge_id", string="Roles", track_visibility='onchange')
    openems_config_update_ids = fields.One2many("openems.openemsconfigupdate", "edge_id", string='OpenEMS Config Updates')
    setup_protocol_ids = fields.One2many('openems.setup_protocol', 'edge_id', 'Setup Protocols')

    # Helper fields
    name_number = fields.Integer(compute="_compute_name_number", store="True")

    @api.depends("name")
    def _compute_name_number(self):
        for rec in self:
            rec.name_number = int(rec.name[4:]) if rec.name.startswith('edge') else -1

    def _get_openems_state_number(self, string):
        state = 0
        if string == "info":
            state = 1
        elif string == "warning":
            state = 2
        elif string == "fault":
            state = 3
        return state

class EdgeUserRole(models.Model):
	_name = "openems.edge_user_role"
	_description = "OpenEMS Edge User Role"
	_sql_constraints = [
		('edge_user_uniq', 'unique(edge_id, user_id)', 'User already exists for this edge.'),
	]
	edge_id = fields.Many2one("openems.edge", string="OpenEMS")
	user_id = fields.Many2one("res.users", string="User")
	role = fields.Selection([
		('admin', 'Admin'),
		('installer', 'Installer'),
		('owner', 'Owner'),
		('guest', 'Guest'),
	], default='guest', required=True)

class OpenemsConfigUpdate(models.Model):
    _name = "openems.openemsconfigupdate"
    _description = "OpenEMS Configuration Update"
    _order = "create_date desc"

    edge_id = fields.Many2one("openems.edge", string="OpenEMS")
    teaser = fields.Text("Update Details Teaser")
    details = fields.Html('Update Details')
