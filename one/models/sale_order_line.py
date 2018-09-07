# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
import logging
logger = logging.getLogger(__name__)

class FasSaleOrderLine(models.Model):
  _inherit = 'sale.order.line'

  charged_to = fields.Selection(string="Charged to", required=True,
    selection=[('warranty','Warranty'),
      ('customer','Customer'),
      ('internal','Internal'),
      ('add-on-costs','Add-On-Costs')])
  fu_id = fields.Many2one(string="FOTON Number", comodel_name="view.fas.fu")
  one_charged_to = fields.Selection(string="Charged to", 
    selection=[('warranty','Warranty'),
      ('customer','Customer'),
      ('internal','internal')])
  discount_amount = fields.Float(string="Discount (Amount)", digits=dp.get_precision('Product Price'))
  part_number = fields.Many2one(string="Part Number", comodel_name="product.product")
  parts_and_jobs = fields.Many2one(string="Parts & Labor", comodel_name="product.product")
  units_and_addons = fields.Many2one(string="Units & Addons", comodel_name="product.product")
  
  @api.onchange("discount_amount")  
  def DiscountAmountChanged(self):    
    if self.price_unit:      
      self.discount = (self.discount_amount / (self.price_unit * self.product_uom_qty)) * 100
  
  @api.onchange("discount")  
  def DiscountPercentChanged(self):
    if self.price_unit:
      self.discount_amount = (self.product_uom_qty * self.price_unit) - self.price_total

  @api.onchange("part_number")
  @api.depends("product_id")
  def OnChangedPartNumber(self):
    self.product_id = self.part_number
    self.product_id_change()

  @api.onchange("parts_and_jobs")
  @api.depends("product_id")
  def OnChangedPartsAndLabor(self):
    self.product_id = self.parts_and_jobs
    self.product_id_change()

  @api.onchange("units_and_addons")
  @api.depends("product_id")
  def OnChangedUnitsAndAddons(self):
    self.product_id = self.units_and_addons
    self.product_id_change()

  @api.onchange("one_charged_to")
  @api.depends("charged_to")
  def oneChargedToChanged(self):
    #if self.one_charged_to:
    self.charged_to = self.one_charged_to or 'warranty'
    logger.info("Charged to: " + self.charged_to)  

  @api.multi
  def name_get(self):
    result = []
    for so_line in self:
      result.append((so_line.id, '[%s] %s' % (so_line.order_id.name, so_line.order_id.partner_id.name)))
    return result

FasSaleOrderLine()
