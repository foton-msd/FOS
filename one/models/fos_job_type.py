# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class FosJobType(models.Model):
  _name = 'fos.job.type'

  name = fields.Char(string="Job Type", required="True")

FosJobType()