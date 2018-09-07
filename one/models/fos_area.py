# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class fasArea(models.Model):
  _name = 'fas.area'

  name = fields.Char(string="Area", required=True)

fasArea()

