# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class FMPIPartsandJobs(models.Model):
  _name = 'fmpi.vqir.parts.and.jobs'

  name = fields.Char(string="ID", readonly=True)
  fmpi_vqir_id = fields.Many2one(string="V.Q.I.R.", comodel_name="fmpi.vqir", readonly=True)
  si_number = fields.Char(string="S.I. Number", readonly=True)
  si_date = fields.Date(string="S.I. Date", readonly=True)
  parts_number = fields.Char(string="Parts Number", readonly=True)
  parts_desc = fields.Char(string="Parts Description", readonly=True)
  parts_qty = fields.Float(string="Quantity", readonly=True)
  parts_cost = fields.Float(string="U/Price", readonly=True)
  parts_with_fee = fields.Boolean(string="With 10% handling fee", readonly=True)
  parts_hf_amount = fields.Float(string="HF Amount")
  parts_total = fields.Float(string="Parts Net Total", readonly=True)
  job_code = fields.Char(string="Job Code", readonly=True)
  job_code_desc = fields.Char(string="Job Desc", readonly=True)
  job_qty = fields.Float(string="Job Qty", readonly=True)
  job_cost = fields.Float(string="Job Cost", digits=dp.get_precision('Product Price'), readonly=True)
  job_total = fields.Float(string="Job Total", compute="_getJobTotal", readonly=True)
  job_parts_total = fields.Float(string="Total", compute="_getJobPartsTotal", readonly=True)
  approved_amount = fields.Float(string="Approved Amount")
  part_id = fields.Many2one(string="Part Number", comodel_name="product.product", readonly=True)
  job_id = fields.Many2one(string="Job Code", comodel_name="product.product", readonly=True)
  parts_approved_amount = fields.Float(string="Approved Amount")
  job_approved_amount = fields.Float(string="Approved Amount")
  dealer_pj_id = fields.Integer(string="Dealer PJ ID")

  @api.onchange("job_qty","job_cost")
  def job_total_changed(self):
    self._getJobTotal()
    self._getJobPartsTotal()

  @api.onchange("parts_qty","parts_cost","parts_with_fee")
  def parts_total_changed(self):
    self._getPartsTotal()
    self._getJobPartsTotal()

  @api.onchange("part_id")
  def ChangeParts(self):
    if self.part_id:
      self.parts_desc = self.part_id.description

  @api.one
  def _getJobTotal(self):
    self.job_total = (self.job_qty or 0) * (self.job_cost or 0)

  @api.one
  def _getJobPartsTotal(self):
    self.job_parts_total = (self.job_total or 0) + (self.parts_total or 0)

  @api.one
  def _getPartsTotal(self):
    self.parts_total = (self.parts_cost or 0) * (self.parts_qty or 0)
    self.parts_net = self.parts_total
    if self.parts_with_fee:
      self.parts_total = self.parts_total * 1.1

  @api.one
  def HFAmount(self):
    self.parts_hf_amount = 0
    if self.parts_with_fee:   
      self.parts_hf_amount = (self.parts_cost * self.parts_qty) * 0.1
    return
   
FMPIPartsandJobs()
