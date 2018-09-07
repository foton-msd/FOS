# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FASProductAttributeValue(models.Model):
  _inherit = 'product.attribute.value'

  description = fields.Char(string="Description")

FASProductAttributeValue()
