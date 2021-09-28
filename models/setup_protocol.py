from odoo import models, fields, _

class SetupProtocol(models.Model):
    _name = "openems.setup_protocol"
    _description = "OpenEMS Setup Protocols (IBN)"
    _order = "create_date desc"

    customer_id = fields.Many2one('res.partner', 'Customer', required=True)
    different_location_id = fields.Many2one('res.partner', 'Different Location')
    installer_id = fields.Many2one('res.partner', 'Installer', required=True)
    edge_id = fields.Many2one('openems.edge', 'OpenEMS', required=True)
    productionlot_ids = fields.One2many('openems.setup_protocol_production_lot', 'setup_protocol_id', 'Serial Numbers')
    item_ids = fields.One2many('openems.setup_protocol_item', 'setup_protocol_id', 'Entry Items')

class SetupProtocolProductionLot(models.Model):
    _name = "openems.setup_protocol_production_lot"
    _description = "OpenEMS Setup Protocol Serial Number"
    _order = "setup_protocol_id, category, sequence asc"

    sequence = fields.Integer("Sort")
    category = fields.Char("Category")
    name = fields.Char("Name")
    lot_id = fields.Many2one('stock.production.lot', 'Serial Number')
    setup_protocol_id = fields.Many2one('openems.setup_protocol', 'Setup Protocol', ondelete='cascade')

class SetupProtocolItem(models.Model):
    _name = "openems.setup_protocol_item"
    _description = "OpenEMS Setup Protocol Entry Item"
    _order = "setup_protocol_id, category, sequence asc"

    sequence = fields.Integer("Sort")
    category = fields.Char("Category")
    name = fields.Char("Name")
    value = fields.Char("Value")
    setup_protocol_id = fields.Many2one('openems.setup_protocol', 'Setup Protocol', ondelete='cascade')
