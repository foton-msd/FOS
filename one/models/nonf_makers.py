# -*- coding: utf-8 -*-
from odoo import models, fields

class NonFotonMakers(models.Model):
  _name = 'nonf.makers'
  _description = 'Non-FOTON Makers'
  _sql_constraints = [('unique_maker','UNIQUE(name)',"Maker already existing"),]

  name = fields.Char(string="Make", required=True)
  model_ids = fields.One2many(string="Models", comodel_name="nonf.models", inverse_name="maker_id")
NonFotonMakers()

class NonFotonModels(models.Model):
  _name = "nonf.models"
  _description = "Non-FOTON Models"
  _sql_constraints = [('unique_maker_model','UNIQUE(name, maker_id)',"Maker Model already existing"),]

  name = fields.Char(string="Model", required=True)
  maker_id = fields.Many2one(string="Maker", comodel_name="nonf.makers", required=True)

NonFotonModels()