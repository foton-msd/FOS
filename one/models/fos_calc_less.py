# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class FOSCalcLess(models.Model):
  _name = 'fos.calc.less'
  _description = 'Less Discount'

  fos_calc_id = fields.Many2one(string="FOS Calculator", comodel_name="fos.calc")
  product_id = fields.Many2one(string='Less', comodel_name='product.product')
  description = fields.Text(string='Description', related="product_id.product_tmpl_id.description", readonly=True)
  amount_less = fields.Float('Amount', digits=dp.get_precision('Product Price'), default=0.0)

  @api.onchange("product_id")
  def product_changed(self):
    if self.product_id:
      self.amount_less = self.product_id.product_tmpl_id.list_price
      
FOSCalcLess()