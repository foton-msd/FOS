# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FosAccountPayment(models.Model):
  _inherit = 'account.payment'
  
  note = fields.Text('Notes')

FosAccountPayment()
