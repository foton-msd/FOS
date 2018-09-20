# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FosPaymentRegister(models.TransientModel):
  _inherit = 'account.register.payments'
  
  note = fields.Text('Notes')

FosPaymentRegister()
