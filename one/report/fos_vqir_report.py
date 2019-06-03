# -*- coding: utf-8 -*- 
from odoo import tools 
from odoo import api, fields, models

class VqirReport1(models.Model):
  _name = 'view.fos.vqir.report' 
  _description = 'VQIR Report'
  _auto = False

  name = fields.Char(string="VQIR Number")
  vqir_date = fields.Datetime(string="VQIR Date")
  fos_fu_id = fields.Many2one(string="FOTON Number", comodel_name="one.fu")
  fu_chassis_number = fields.Char(string="Chassis Number", related="fos_fu_id.chassis_number")
  fu_engine_number = fields.Char(string="Engine Number", related="fos_fu_id.engine_number")
  users_name = fields.Char(string="User's Name")
  users_mobile = fields.Char(string="Phone")
  run_km = fields.Integer(string="Run KM")
  date_occur = fields.Date(string="Date of occurence")
  km_1st_trouble = fields.Integer(string="KM of first trouble happened")
  trouble_cause_analysis = fields.Text(string="Trouble Cause Analysis")
  disposal_measures = fields.Text(string="Disposal Measures")
  date_occur = fields.Date(string="Date of occurence")
  parts_number = fields.Char(string="Part Number")
  parts_desc = fields.Char(string="Parts Description")
  parts_qty = fields.Float(string="Quantity")
  parts_cost = fields.Float(string="U/Price")
  parts_hf_amount = fields.Float(string="HF Amount")
  parts_total = fields.Float(string="Parts Total")
  job_code = fields.Char(string="Job Code")
  job_code_desc = fields.Char(string="Job Desc")
  job_qty = fields.Float(string="Job Qty")
  job_cost = fields.Float(string="Job Cost")
  job_total = fields.Float(string="Job Total")
  job_parts_total = fields.Float(string="Total")
  remarks = fields.Char(string="Remarks")
  dealer_id = fields.Many2one(string="Dealer", comodel_name="one.dealers")
  vqir_state = fields.Selection(string="Status", 
    selection=[('draft', 'Draft'),('cancel', 'Cancelled'),('submit', 'Submitted'),
    ('ack', 'Acknowledged'),('approved', 'Approved'),('declined', 'Returned'),('disapproved', 'Disapproved'),('paid', 'Paid')])

  @api.model_cr
  def init(self):
      tools.drop_view_if_exists(self.env.cr, "fmpi_vqir_report")
      self.env.cr.execute("""
            CREATE OR REPLACE VIEW view_fos_vqir_report AS
            SELECT a.id, a.name, a.vqir_date, a.fos_fu_id,
                          b.chassis_number, b.engine_number, a.users_name,
                          a.users_mobile, a.km_1st_trouble, a.run_km, a.date_occur,
                          a.trouble_cause_analysis, a.disposal_measures, d.job_code_desc, d.job_code,
                          d.parts_number, d.parts_desc, d.parts_with_fee, d.parts_qty, d.parts_cost,
                          ((d.parts_qty * d.parts_cost) * case when d.parts_with_fee then 1.1 else 1 end)::float as parts_total,
                          ((d.parts_cost * d.parts_qty) * 0.1)::float as parts_hf_amount,
                          d.job_qty, d.job_cost, (d.job_qty * d.job_cost)::float as job_total, 
    
              (((d.parts_qty * d.parts_cost) * case when d.parts_with_fee then 1.1 else 1 end)::float +
              (d.job_qty * d.job_cost)::float)::float as job_parts_total,

                          b.fmpi_fu_local_name_id, a.remarks,
                          a.ss_name, a.dealer_id, a.vqir_state,
                          c.id AS one_fu_local_name_id, d.id AS ovpj_id
                          FROM fmpi_vqir a
                          LEFT JOIN one_fu b ON a.fos_fu_id = b.id
                          LEFT JOIN one_local_names c ON b.fmpi_fu_local_name_id = c.id
                          LEFT JOIN fmpi_vqir_parts_and_jobs d on a.id = d.fmpi_vqir_id;
               """)
VqirReport1()