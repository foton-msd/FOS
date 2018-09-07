# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class FMPIPartsandJobs(models.Model):
  _name = 'fmpi.vqir.parts.and.jobs'

  name = fields.Char(string="ID", readonly=True)
  fmpi_vqir_id = fields.Many2one(string="V.Q.I.R.", comodel_name="fmpi.vqir", readonly=True)
  si_number = fields.Char(string="S.I. Number", readonly=True)
  si_date = fields.Date(string="S.I. Date", readonly=True)
  parts_number = fields.Char(string="Parts Number", readonly=True)
  parts_desc = fields.Char(string="Parts", readonly=True)
  parts_qty = fields.Float(string="Quantity", readonly=True)
  parts_cost = fields.Float(string="U/Price", readonly=True)
  parts_with_fee = fields.Boolean(string="With 10% handling fee", readonly=True)
  parts_total = fields.Float(string="Parts Net Total", readonly=True)
  job_code = fields.Char(string="Job Code", readonly=True)
  job_code_desc = fields.Char(string="Job Desc", readonly=True)
  job_qty = fields.Float(string="Job Qty", readonly=True)
  job_cost = fields.Float(string="Job Cost", readonly=True)
  job_total = fields.Float(string="Job Total", readonly=True)
  job_parts_total = fields.Float(string="Sub Total", readonly=True)
  remarks = fields.Text(string="Remarks", readonly=True)

FMPIPartsandJobs()
