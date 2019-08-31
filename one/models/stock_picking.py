# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class StockPicking(models.Model):
  _inherit = 'stock.picking'

  total_product_qty = fields.Float(string="Total Qty", compute="_getTotalQty", digits=dp.get_precision('Product Unit of Measure'))

  @api.one
  def _getTotalQty(self):
    for line in self.move_line_ids:
       self.total_product_qty += line.qty_done
       
  @api.multi
  def print_picking_list(self):
    return self.env.ref('one.report_picking_list').report_action(self) 

StockPicking()