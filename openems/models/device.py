from odoo import api, fields, models
from datetime import datetime

class Device(models.Model):
    _name = "openems.device"
    _description = "OpenEMS Edge Device"
    _inherit = "mail.thread"
    _order = "name_number asc"
    _sql_constraints = [
        ("unique_name", "unique(name)", "Name needs to be unique"),
        ("unique_stock_production_lot_id", "unique(stock_production_lot_id)",
         "Serial number needs to be unique")
    ]

    name = fields.Char(required=True)
    active = fields.Boolean("Active", default=True, tracking=True)
    comment = fields.Char(tracking=True)
    internalnote = fields.Text("Internal note", tracking=True)
    tag_ids = fields.Many2many("openems.device_tag", string="Tags", tracking=True)
    monitoring_url = fields.Char(
        "Online-Monitoring", compute="_compute_monitoring_url", store=False
    )
    stock_production_lot_id = fields.Many2one("stock.lot")
    first_setup_protocol_date = fields.Datetime(
        "First Setup Protocol Date", compute="_compute_first_setup_protocol"
    )
    manual_setup_date = fields.Datetime("Manual Setup Date")

    @api.depends("setup_protocol_ids", "manual_setup_date")
    def _compute_first_setup_protocol(self):
        for rec in self:
            if rec.manual_setup_date:
                rec.first_setup_protocol_date = rec.manual_setup_date
            elif len(rec.setup_protocol_ids) > 0:
                rec.first_setup_protocol_date = rec.setup_protocol_ids[
                    (len(rec.setup_protocol_ids) - 1)
                ]["create_date"]
            else:
                rec.first_setup_protocol_date = None

    @api.depends("name")
    def _compute_monitoring_url(self):
        for rec in self:
            url = self.env["ir.config_parameter"].sudo().get_param("openems.edge_monitoring_url", default='#')
            rec.monitoring_url = url + rec.name

    producttype = fields.Selection(
        [
            ("openems-edge", "OpenEMS Edge"),
        ],
        "Product type",
        tracking=True,
    )
    emshardware = fields.Selection([], "EMS Hardware", tracking=True)
    oem = fields.Selection(
        [
            ("openems", "OpenEMS"),
        ],
        "OEM Branding",
        default="openems",
    )

    # Settings
    openems_config = fields.Text("OpenEMS Config Full")
    openems_config_components = fields.Text("OpenEMS Config")
    openems_version = fields.Char("OpenEMS Version", tracking=True)

    # Security
    setup_password = fields.Char(
        "Installateursschlüssel (Installation key)",
        help="Passwort für die Inbetriebnahme durch den Installateur",
    )
    apikey = fields.Char("API-Key", required=True, tracking=True)

    # 'openems_sum_state_level' is updated by OpenEMS Backend
    openems_sum_state_level = fields.Selection(
        [("ok", "Ok"), ("info", "Info"), ("warning", "Warning"), ("fault", "Fault")],
        "OpenEMS State",
    )
    # 'openems_is_connected' is updated by OpenEMS Backend
    openems_is_connected = fields.Boolean("OpenEMS Is connected")

    # System Status
    lastmessage = fields.Datetime("Last message")
    lastupdate = fields.Datetime("Last data update")

    # Verknüpfungen
    systemmessage_ids = fields.One2many(
        "openems.systemmessage", "device_id", string="Systemmessages"
    )
    user_role_ids = fields.One2many(
        "openems.device_user_role", "device_id", string="Roles", tracking=True
    )
    alerting_settings = fields.One2many(
        "openems.alerting", "device_id", string="Alerting", tracking=True
    )
    openems_config_update_ids = fields.One2many(
        "openems.openemsconfigupdate", "device_id", string="OpenEMS Config Updates"
    )
    setup_protocol_ids = fields.One2many(
        "openems.setup_protocol", "device_id", "Setup Protocols"
    )

    # Helper fields
    name_number = fields.Integer(compute="_compute_name_number", store="True")

    @api.depends("name")
    def _compute_name_number(self):
        for rec in self:
            rec.name_number = int(rec.name[4:]) if rec.name.startswith("edge") else -1

    def _get_openems_state_number(self, string):
        state = 0
        if string == "info":
            state = 1
        elif string == "warning":
            state = 2
        elif string == "fault":
            state = 3
        return state

    @api.model
    def create(self, vals):
        # Generate API key if not provided
        if 'apikey' not in vals or not vals['apikey']:
            vals['apikey'] = self._generate_api_key()

        return super(Device, self).create(vals)

    def _generate_api_key(self):
        # Generate a random API key in the format you specified
        return ''.join(random.choices(string.ascii_letters + string.digits, k=20))


class DeviceTag(models.Model):
    _name = "openems.device_tag"
    _description = "OpenEMS Edge Device Tag"
    name = fields.Char(required=True)


class DeviceUserRole(models.Model):
    _name = "openems.device_user_role"
    _description = "OpenEMS Edge Device User Role"
    _sql_constraints = [
        (
            "device_user_uniq",
            "unique(device_id, user_id)",
            "User already exists for this device.",
        ),
    ]
    device_id = fields.Many2one("openems.device", string="OpenEMS Edge")
    user_id = fields.Many2one("res.users", string="User")
    role = fields.Selection(
        [
            ("admin", "Admin"),
            ("installer", "Installer"),
            ("owner", "Owner"),
            ("guest", "Guest"),
        ],
        default="guest",
        required=True,
    )


class OpenemsConfigUpdate(models.Model):
    _name = "openems.openemsconfigupdate"
    _description = "OpenEMS Edge Device Configuration Update"
    _order = "create_date desc"

    device_id = fields.Many2one("openems.device", string="OpenEMS Edge")
    teaser = fields.Text("Update Details Teaser")
    details = fields.Html("Update Details")


class Systemmessage(models.Model):
    _name = "openems.systemmessage"
    _description = "OpenEMS Edge Systemmessage"
    _order = "create_date desc"

    timestamp = fields.Datetime("Creation date")
    device_id = fields.Many2one("openems.device", string="OpenEMS Edge")
    text = fields.Text("Message")
    text_teaser = fields.Char(compute="_compute_text_teaser")

    @api.depends("text")
    def _compute_text_teaser(self):
        for rec in self:
            # get up to 100 characters from first line
            rec.text_teaser = rec.text.splitlines()[0][0:100] if rec.text else False

class Alerting(models.Model):
    _name = "openems.alerting"
    _description = "OpenEMS Edge AlertingSettings"
    _sql_constraints = [
        (
            "device_user_uniq",
            "unique(device_id, user_id)",
            "User already has Alerting Settings.",
        ),
    ]

    device_id = fields.Many2one("openems.device", string="OpenEMS Edge")
    user_id = fields.Many2one("res.users", string="User")

    offline_delay = fields.Integer(string="Offline Notification", default=1440)
    warning_delay = fields.Integer(string="Warning Notification", default=1440)
    fault_delay = fields.Integer(string="Fault Notification", default=1440)

    offline_last_notification = fields.Datetime(string="Last Offline notification sent")
    sum_state_last_notification = fields.Datetime(string="Last SumState notification sent")

    device_name = fields.Text(compute="_compute_device_name", store="True")
    user_login = fields.Text(compute="_compute_user_login", store="True")

    user_role = fields.Selection(
        [("admin", "Admin"), ("installer", "Installer"), ("owner", "Owner"), ("guest", "Guest"),],
        compute="_compute_user_role", store="False")

    @api.depends("device_id")
    def _compute_device_name(self):
        for rec in self:
            rec.device_name = rec.device_id.name;

    @api.depends("user_id")
    def _compute_user_login(self):
        for rec in self:
            rec.user_login = rec.user_id.login;

    @api.depends("user_id", "device_id")
    def _compute_user_role(self):
        for rec in self:
            user_role: DeviceUserRole = rec.user_id.device_role_ids.search([('device_id','=',rec.device_id.id)])
            if user_role:
                return user_role.role
            else:
                return rec.user_id.global_role
