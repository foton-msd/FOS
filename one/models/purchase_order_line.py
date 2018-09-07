# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class FasPurchaseOrderLine(models.Model):
  _name = 'purchase.order.line'
  _inherit = 'purchase.order.line' 

  fu_id = fields.Many2one(string="P.O. for FOTON Number", comodel_name="view.fas.fu")
  fos_fu_ids = fields.One2many(string="FOTON Units", comodel_name="view.fas.fu", inverse_name="po_line_id")	

  @api.multi
  def name_get(self):
    result = []
    for event in self:
      result.append((event.id, '[%s] %s' % (event.order_id.name, event.product_id.name)))
    return result

FasPurchaseOrderLine()
