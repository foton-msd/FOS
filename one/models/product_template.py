# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
import logging
logger = logging.getLogger(__name__)

class FASProduct(models.Model):
  _inherit = 'product.template'
  _sql_constraints = [
    ('product_labor_unique', 'unique(name,sub_type)','Product already exists!')
  ]

  sub_type = fields.Selection(string="Sub-type", selection=[('units','Units'),('parts','Parts'),('supplies','Supplies'),('labor','Labor'),('merchandise','Merchandise'),('warranty','Warranty')])
  unit_class = fields.Selection(string="Unit Classification", 
    selection=[('pv','PV'),('ldt','LDT'),('he','HE'),('hdt','HDT'),('gratour','GRATOUR'),
    ('trailer','TRAILER'),('genset','GENSET'), ('bu-pv','BU-PV'),('bu-ldt','BU-LDT'),('bu-he','BU-HE'),('bu-hdt','BU-HDT')])
  isc = fields.Float(string="ISC")
  fob_php = fields.Float(string="FOB PHP")
  fob_usd = fields.Float(string="FOB USD")
  fob_rmb = fields.Float(string="FOB RMB")
  dnp = fields.Float(string="DNP (Dealer's SRP)")
  loc1 = fields.Char(string="Location 1")
  loc2 = fields.Char(string="Location 2")
  loc3 = fields.Char(string="Location 3")
  loc4 = fields.Char(string="Location 4")
  loc5 = fields.Char(string="Location 5")
  loc6 = fields.Char(string="Location 6")
  loc7 = fields.Char(string="Location 7")
  loc8 = fields.Char(string="Location 8")
  loc9 = fields.Char(string="Location 9")
  model = fields.Char(string="Model")
  model_code = fields.Char(string="Model Code")
  inner_code = fields.Char(string="Inner Code")
  segment = fields.Char(string="Segment")
  fmpi_product = fields.Boolean(string="FMPI Product", default=False, copy=False)
  fmpi_product_id = fields.Integer(string="Product")
  fmpi_product_write_date = fields.Datetime(string="Write Stamp")
  run_by_sync = fields.Boolean(string="Run by sync")
  no_of_hours = fields.Float(string="No. of Hours", digits=dp.get_precision('Product Price'))
  is_fmpi = fields.Boolean(string="Is FMPI", related='company_id.is_fmpi')
  
  @api.multi
  def write(self, values):    
    if 'fmpi_product' in values and values['fmpi_product']:        
      if 'run_by_sync' in values and not values['run_by_sync']:
        raise UserError(("You cannot modify detail of FMPI Products!"))
      else:
        values['run_by_sync'] = False
        super(FASProduct, self).write(values)
    else:
      values['run_by_sync'] = False
      super(FASProduct, self).write(values)
   

FASProduct()
