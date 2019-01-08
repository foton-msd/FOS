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
      ('first_pms','First PMS'),
      ('tsb','TSB'),
      ('add-on-costs','Add-On-Costs')])
  fu_id = fields.Many2one(string="FOTON Number", comodel_name="one.fu")
#  one_charged_to = fields.Selection(string="Charged to", 
#    selection=[('warranty','Warranty'),
#      ('customer','Customer'),
#      ('internal','internal')])
  discount_amount = fields.Float(string="Discount (Amount)", digits=dp.get_precision('Discount'))
  part_number = fields.Many2one(string="Part Number", comodel_name="product.product")
  parts_and_jobs = fields.Many2one(string="Parts & Labor", comodel_name="product.product")
  units_and_addons = fields.Many2one(string="Units & Addons", comodel_name="product.product")
  part_desc = fields.Text(string="Parts Description", related="product_id.product_tmpl_id.description_sale", readonly=True)

  @api.onchange("discount_amount")  
  def DiscountAmountChanged(self):    
    if self.price_unit:
      self.discount = (self.discount_amount / (self.price_unit * self.product_uom_qty)) * 100    

  @api.onchange("discount")  
  def DiscountPercentChanged(self):    
    if self.price_unit:
      self.discount_amount = (self.product_uom_qty * self.price_unit) * (self.discount / 100)

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
    if self.product_id:
      lc_obj = self.env['fos.labor.codes'].browse([
        ('one_local_name_id','=',self.order_id.fu_local_name_id.id)
        ])
      if lc_obj:
        for lc1 in lc_obj:
          self.product_uom_qty = lc1.no_of_hours
          pp_obj = self.env['product.product'].search(['id','=',self.product_id.id])
          if pp_obj:
            for pp in pp_obj:
              pp.write({'list_price': lc1.flat_rate})
          self.price_unit = lc1.flat_rate

          logger.info("flat_rate:" + str(lc1.flat_rate))
          logger.info("price_unit:" + str(self.price_unit))
      
  @api.onchange("units_and_addons")
  @api.depends("product_id")
  def OnChangedUnitsAndAddons(self):
    self.product_id = self.units_and_addons
    self.product_id_change()

#  @api.onchange("one_charged_to")
#  @api.depends("charged_to")
#  def oneChargedToChanged(self):
    #if self.one_charged_to:
#    self.charged_to = self.one_charged_to or 'warranty'
#    logger.info("Charged to: " + self.charged_to)  

  @api.multi
  def name_get(self):
    result = []
    for so_line in self:
      result.append((so_line.id, '[%s] %s' % (so_line.order_id.name, so_line.order_id.partner_id.name)))
    return result

FasSaleOrderLine()
