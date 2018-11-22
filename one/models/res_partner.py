# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class FasResPartner(models.Model):
  _inherit = 'res.partner'
  _sql_constraints = [
      ('unique_name', 'unique(name)', 'Partner Name already exists!')
  ]
  imm_contact = fields.Char(string="Immediate Contact Person")
  customer_type_units = fields.Boolean(string="Units")
  customer_type_parts_and_service = fields.Boolean(string="Parts & Service")
  fax = fields.Char(string="Fax")
  over_credit = fields.Boolean('Allow Over Credit?')
  
FasResPartner()