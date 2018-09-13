# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class FasPartsandJobs(models.Model):
  _name = 'fos.vqir.parts.and.jobs'

  name = fields.Char(string="ID", required=True, readonly=True, default='auto-generated')
  fos_vqir_id = fields.Many2one(string="V.Q.I.R.", comodel_name="fos.vqir", required=True)
  si_number = fields.Char(string="S.I. Number")
  si_date = fields.Date(string="S.I. Date")
  parts_number = fields.Char(string="Parts Number")
  parts_desc = fields.Char(string="Parts")
  parts_qty = fields.Float(string="Quantity")
  parts_cost = fields.Float(string="U/Price")
  parts_with_fee = fields.Boolean(string="With 10% handling fee")
  parts_hf_amount = fields.Float(string="HF Amount", compute="HFAmount", readonly=True)
  parts_total = fields.Float(string="Parts Net Total", compute='_getPartsTotal', readonly=True)
  job_code = fields.Char(string="Job Code")
  job_code_desc = fields.Char(string="Job Desc")
  job_qty = fields.Float(string="Job Qty")
  job_cost = fields.Float(string="Job Cost")
  job_total = fields.Float(string="Job Total", compute="_getJobTotal", readonly=True)
  job_parts_total = fields.Float(string="Total", compute="_getJobPartsTotal", readonly=True)
  
  @api.onchange("job_qty","job_cost")
  def job_total_changed(self):
    self._getJobTotal()
    self._getJobPartsTotal()

  @api.onchange("parts_qty","parts_cost","parts_with_fee")
  def parts_total_changed(self):
    self._getPartsTotal()
    self._getJobPartsTotal()

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
  @api.depends("parts_hf_amount")
  def HFAmount(self):
    self.parts_hf_amount = 0
    if self.parts_with_fee:   
      self.parts_hf_amount = (self.parts_cost * self.parts_qty) * 0.1
    return

FasPartsandJobs()
