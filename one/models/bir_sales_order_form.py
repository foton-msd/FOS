# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang

import logging
_logger = logging.getLogger(__name__)

class BIRSalesOrderForm(models.Model):
  _inherit = 'sale.order'

  @api.multi
  def _bir_get_tax_amount_by_group(self):
    self.ensure_one()
    res = {}
    res1 = []
    for line in self.order_line:
      base_tax = 0
      for tax in line.tax_id:
        group = tax.tax_group_id
        res.setdefault(group, {'amount': 0.0, 'base': 0.0, 'name': ''})
        # FORWARD-PORT UP TO SAAS-17
        price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
        taxes = tax.compute_all(price_reduce + base_tax, quantity=line.product_uom_qty,
                product=line.product_id, partner=self.partner_shipping_id)['taxes']
        for t in taxes:
          res[group]['amount'] += t['amount']
          res[group]['base'] += t['base']
          res1.append([t['name'],t['base'],t['amount']])
        if tax.include_base_amount:
          base_tax += tax.compute_all(price_reduce + base_tax, quantity=1, product=line.product_id,
                      partner=self.partner_shipping_id)['taxes'][0]['amount']
    res = sorted(res.items(), key=lambda l: l[0].sequence)
    #res = [(l[0].name, l[1]['amount'], l[1]['base'], len(res)) for l in res]
    res2 = []
    for r in res1:
      tax_name = r[0]
      tax_base = r[1]
      tax_amount = r[2]
      if not res2:
        res2.append([tax_name, tax_base, tax_amount])
      else:
        found = False
        for x in res2:
          if x[0] == tax_name:
            res2[x.index(x[0])][2] += tax_amount
            found = True
        if not found:
          res2.append([tax_name, tax_base, tax_amount])
    return res2

BIRSalesOrderForm()
