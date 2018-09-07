# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_compare, pycompat
from odoo.tools.misc import formatLang
from functools import partial

import logging
_logger = logging.getLogger(__name__)

class BIRAccountInvoiceForm(models.Model):
  _inherit = 'account.invoice'

  @api.multi
  def _bir_get_tax_amount_by_group(self):
    self.ensure_one()
    currency = self.currency_id or self.company_id.currency_id
    fmt = partial(formatLang, self.with_context(lang=self.partner_id.lang).env, currency_obj=currency)
    res = {}
    res1 = []
    for line in self.tax_line_ids:
      res.setdefault(line.tax_id.tax_group_id, {'base': 0.0, 'amount': 0.0})
      res[line.tax_id.tax_group_id]['amount'] += line.amount
      res[line.tax_id.tax_group_id]['base'] += line.base
      res1.append([line.tax_id.name, line.base, line.amount])
    res = sorted(res.items(), key=lambda l: l[0].sequence)
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

BIRAccountInvoiceForm()
