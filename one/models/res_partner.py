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

#  @api.model
#  def create(self, values):
#    to_lower_list = ['tz','email','website','company_type','picking_warn','invoice_warn', 'lang', 'type', 'purchase_warn', 'sale_warn', 'trust']
#    for v in values:
#      if type(values[v]) is str:
#        if not v in to_lower_list:
#          values[v] = str(values[v]).upper()
#        else:
#          logger.info("Variable Name: "+ str(v) + " Type: " + str(type(values[v])))
#    record = super(FasResPartner, self).create(values)
#    return record

#  @api.multi
#  def write(self, values):
#    to_lower_list = ['tz','email','website','company_type','picking_warn','invoice_warn', 'lang', 'type', 'purchase_warn', 'sale_warn', 'trust']
#    for v in values:
#      if type(values[v]) is str:
#        if v in to_lower_list:
#          values[v] = str(values[v]).lower()
#        else:
#          values[v] = str(values[v]).upper()
      #else:
      #  logger.info("Variable Name: "+ str(v) + " Type: " + str(type(values[v])))
#    super(FasResPartner, self).write(values)
  
FasResPartner()