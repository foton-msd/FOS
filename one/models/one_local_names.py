# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LocalNames(models.Model):
  _name = 'one.local.names'
  _description = 'Local Names'

  name = fields.Char(string="Local Name", required=True)
  classification = fields.Char(string="Classification")
  fmpi_fu_local_name_id = fields.Integer(string="FMPI Local Name ID", readonly=True)
  fmpi_fu_local_name_stamp = fields.Datetime(string="FMPI Local Name Stamp", readonly=True)
  one_body_type_ids = fields.One2many(string="Body Types", comodel_name="one.body.types", inverse_name="one_local_name_id")
  active = fields.Boolean(string="Active", default=True)

  @api.multi
  def name_get(self):
    result = []
    for event in self:
        result.append((event.id, '%s [%s]' % (event.name, event.classification)))
    return result

LocalNames()
