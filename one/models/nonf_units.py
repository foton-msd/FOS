# -*- coding: utf-8 -*-

from odoo import models, fields, api

class NonFotonUnits(models.Model):
  _name = 'nonf.units'
  _description = 'Non-FOTON Units'

  name = fields.Char(string="Plate Number")
  conduction_sticker = fields.Char(string="Conduction Sticker")
  maker_id = fields.Many2one(string="Make", comodel_name="nonf.makers", required=True)
  model_id = fields.Many2one(string="Model", comodel_name="nonf.models", required=True)
  description = fields.Char(string="Description")
  engine_number = fields.Char(string="Engine Number")
  chassis_number = fields.Char(string="Chassis Number")
  
  color = fields.Char(string="Color")
  body_type = fields.Char(string="Body Type")
  year_model = fields.Char(string="Year Model")
  owner_name = fields.Char(string="Registered to")
  owner_address = fields.Text(string="Address")
  owner_contact_details = fields.Text(string="Contact Info")

  @api.onchange("maker_id")  
  def OnChangedMakerId(self):
    self.model_id = False
    res = {}
    if self.maker_id:
        res['domain'] = {'model_id': [('maker_id', '=', self.maker_id.id)]}
    return res
    
NonFotonUnits()
