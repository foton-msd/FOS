# -*- coding: utf-8 -*-

from openpyxl import load_workbook
from odoo import models, fields, api
from odoo.tools.translate import _
import logging
logger = logging.getLogger(__name__)

class FasPurchaseOrder(models.Model):
  _inherit = 'purchase.order'

  po_type = fields.Selection(string="P.O. Type", required=True, readonly=True, states={'draft': [('readonly', False)]},
    selection=[('units','Units'),('parts','Parts'),('supplies','Supplies'),('labor','Labor')],
    default='parts')
  contract_date = fields.Date(string="Contract Date", readonly=True, states={'draft': [('readonly', False)]})
  contract_number = fields.Char(string="Contract Number", readonly=True, states={'draft': [('readonly', False)]})


  prepared_by_id = fields.Many2one(string="Prepared by", comodel_name="res.users", default=lambda self: self.env.user, readonly=True)
  prepared_by_desig = fields.Char(string="Designation", related="prepared_by_id.partner_id.function", readonly=True)
  checked_by = fields.Char(string="Checked by")
  approved_by = fields.Char(string="Approved by")
  checked_by_desig = fields.Char(string="Designation")
  approved_by_desig = fields.Char(string="Designation")
  rfq_number = fields.Char(string="RFQ Number", readonly=True)

  @api.multi
  def button_confirm2(self):
    for order in self:
      if order.state not in ['draft', 'sent']:
        continue
      order.write({
        'rfq_number': order.name,
        'name': self.env['ir.sequence'].next_by_code('fas.po.seq')})
      order._add_supplier_to_product()
      # Deal with double validation process
      if order.company_id.po_double_validation == 'one_step'\
        or (order.company_id.po_double_validation == 'two_step'\
        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
        or order.user_has_groups('purchase.group_purchase_manager'):
        order.button_approve()
      else:
        order.write({'state': 'to approve'})
    return True

  @api.multi
  def name_get(self):
    result = []
    for event in self:
      result.append((event.id, '%s [%s] [%s]' % (event.name, event.contract_number or "No Contract Number", event.partner_id.name)))
    return result

  @api.multi
  def get_po_lines(self):
    for order in self:      
      view_id = self.env['purchase.order.line.import']
      new = view_id.create({'order_id': self.id})
      return {
        'type': 'ir.actions.act_window',
        'name': 'Where is your Purchase Order Lines file',
        'res_model': 'purchase.order.line.import',
        'view_type': 'form',
        'view_mode': 'form',
        'res_id': new.id,
        'view_id': self.env.ref('one.fos_purchase_order_line_import_form',False).id,
        'target': 'new',
    }
FasPurchaseOrder()
