# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FosAccountPayment(models.Model):
  _inherit = 'account.payment'
  
  note = fields.Text('Notes')
  cheque_number = fields.Char('Cheque Number')
  payment_received_from = fields.Char(string="Payment Received from")

  @api.onchange("partner_id")
  def partner_changed(self):
      if self.partner_id:
        self.payment_received_from = self.partner_id.name

FosAccountPayment()
