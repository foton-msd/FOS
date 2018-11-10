from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    picking_type_code = fields.Char(string="Code", related="picking_type_id.code", readonly=True)

StockPicking()