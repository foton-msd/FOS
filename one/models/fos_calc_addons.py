# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class FOSCalcAddons(models.Model):
  _name = 'fos.calc.addons'
  _description = 'Additional Accessories'
  _sql_constraints = [('calc_addons_unique', 'unique (fos_calc_id, product_id)','Additional Accessories line already existing!')]

  fos_calc_id = fields.Many2one(string="FOS Calculator", comodel_name="fos.calc")
  product_id = fields.Many2one(string='Addons', comodel_name='product.product')
  description = fields.Text(string='Description', related="product_id.product_tmpl_id.description")
  amount = fields.Float('Amount', digits=dp.get_precision('Product Price'), default=0.0)
    
  @api.onchange("product_id")
  def amount_changed(self):
    if self.product_id:
      self.amount = self.product_id.product_tmpl_id.list_price

FOSCalcAddons()