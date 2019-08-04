# -*- coding: utf-8 -*- 
from odoo import tools 
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp

class VqirReport1(models.Model):
  _name = 'view.fos.vqir.report1' 
  _description = 'VQIR Report-1'
  _auto = False

  name = fields.Char(string="ID", readonly=True)
  fmpi_vqir_id = fields.Many2one(string="V.Q.I.R.", comodel_name="fmpi.vqir", readonly=True)
  si_number = fields.Char(string="S.I. Number", readonly=True)
  si_date = fields.Date(string="S.I. Date", readonly=True)
  vqir_date = fields.Date(string="VQIR Date", readonly=True)
  parts_number = fields.Char(string="Parts Number", readonly=True)
  parts_desc = fields.Char(string="Parts Description", readonly=True)
  parts_qty = fields.Float(string="Quantity", readonly=True)
  parts_cost = fields.Float(string="U/Price", readonly=True)
  #parts_with_fee = fields.Boolean(string="With 10% handling fee", readonly=True)
  parts_hf_amount = fields.Float(string="HF Amount")
  parts_total = fields.Float(string="Parts Net Total", readonly=True)
  job_code = fields.Char(string="Job Code", readonly=True)
  job_code_desc = fields.Char(string="Job Desc", readonly=True)
  job_qty = fields.Float(string="Job Qty", readonly=True)
  job_cost = fields.Float(string="Job Cost", digits=dp.get_precision('Product Price'), readonly=True)
  #job_total = fields.Float(string="Job Total", compute="_getJobTotal", readonly=True)
  #job_parts_total = fields.Float(string="Total", compute="_getJobPartsTotal", readonly=True)
  approved_amount = fields.Float(string="Parts Approved Amount")
  part_id = fields.Many2one(string="Part Number", comodel_name="product.product", readonly=True)
  job_id = fields.Many2one(string="Job Code", comodel_name="product.product", readonly=True)
  job_approved_amount = fields.Float(string="Job Approved Amount")
  #job_parts_approved_total = fields.Float(string="Total", compute="_getJobPartsApprovedTotal", readonly=True)
  dealer_pj_id = fields.Integer(string="Dealer PJ ID")
  dealer_id = fields.Many2one(string="Dealer", comodel_name="one.dealers")
  vqir_state = fields.Selection(string="Status", 
    selection=[('draft', 'Draft'),('cancel', 'Cancelled'),('submit', 'Submitted'),
    ('ack', 'Acknowledged'),('approved', 'Approved'),('declined', 'Returned'),('disapproved', 'Disapproved'),('paid', 'Paid')])

  @api.model_cr
  def init(self):
      tools.drop_view_if_exists(self.env.cr, "fmpi_vqir_report1")
      self.env.cr.execute("""
            CREATE OR REPLACE VIEW view_fos_vqir_report AS
      select a.*,b.id as dealer_id, b.vqir_state, b.vqir_date
      from fmpi_vqir_parts_and_jobs a
      left join fmpi_vqir b on a.fmpi_vqir_id = b.id

      where not b.id isnull;
               """)
VqirReport1()