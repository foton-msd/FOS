# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
import logging
logger = logging.getLogger(__name__)

class FOSSaleCalculator(models.Model):
  _name = 'fos.calc'
  _description = 'Sale Calculator'

  name = fields.Char(string="Sale Calculator", required=True, default='Auto-generated', readonly=True, copy=False)
  unit_id = fields.Many2one(string="Unit", comodel_name="product.product")
  customer_id = fields.Many2one(string="Customer", comodel_name="res.partner", required=True)
  srp = fields.Float('SRP', digits=dp.get_precision('Product Price'), default=0.0, related="unit_id.product_tmpl_id.list_price")
  less_discount = fields.Float('Less Discount', default=0.0)
  net_cash = fields.Float(string="Net Cash", compute="_getNetCash", readonly=True)
  downpayment = fields.Float('Downpayment')
  dp_percent = fields.Float('DP (%)', compute="_getDPPercentage", readonly=True)
  amount_financed = fields.Float('Amount Finance', compute="_getAmountFinanced", readonly=True)
  reservation_fee = fields.Float('Reservation Fee')
  bank_id = fields.Many2one(string="Bank", comodel_name="fos.calc.banks")
  s_term = fields.Integer(string="TERM(months)", related="bank_id.standard_term")
  o_term = fields.Integer(string="TERM(months)", related="bank_id.oma_term")
  std_bank = fields.Float(string="Bank Standard", related="bank_id.bank_std") 
  oma_bank = fields.Float(string="Bank OMA", related="bank_id.bank_oma") 
  monthly_amortization_std = fields.Float('Montly Amortization', compute="_getMonthlyAmortizationstd", readonly=True)
  monthly_amortization_oma = fields.Float('Montly Amortization', compute="_getMonthlyAmortizationoma", readonly=True)
  cash_outlay = fields.Selection(string="Cash Outlay", selection=[('standard', 'Standard'),('oma','OMA')], required=True)
  insurance_std = fields.Float(string='Insurance', related="unit_id.insurance_std")
  chattel_mortgage_std = fields.Float(string="Chattel and Mortgage", related="unit_id.chattel_mortgage_std")
  lto_registration_std = fields.Float(string='LTO Registration', related="unit_id.lto_registration_std")
  insurance_oma = fields.Float(string='Insurance', related="unit_id.insurance_oma")
  chattel_mortgage_oma = fields.Float(string="Chattel and Mortgage", related="unit_id.chattel_mortgage_oma")
  lto_registration_oma = fields.Float(string='LTO Registration', related="unit_id.lto_registration_oma")
  oma_oma = fields.Float(string="OMA", compute="_getMonthlyAmortizationoma", readonly=True)
  oma_std = fields.Float(string="OMA")
  addons = fields.One2many(string="Product", comodel_name="fos.calc.addons", inverse_name="fos_calc_id", ondelete='cascade', index=True, copy=False)
  addons_total = fields.Float(string="Additional Accessories", compute="_getAddonsTotal", readonly=True)
  less = fields.One2many(string="Product", comodel_name="fos.calc.less", inverse_name="fos_calc_id", ondelete='cascade', index=True, copy=False)
  less_total = fields.Float(string="Less", compute="_getLessTotal", readonly=True)
  net_cash_outlay_std = fields.Float(string="Net Cash Outlay", compute="_getNCOStd", readonly=True)
  net_cash_outlay_oma = fields.Float(string="Net Cash Outlay", compute="_getNCOOma", readonly=True)

  @api.one
  def _getNetCash(self):
    self.net_cash = (self.srp or 0) - (self.less_discount or 0)

  @api.one
  def _getDPPercentage(self):
   if self.srp > 0:
    self.dp_percent = ((self.downpayment or 0) / (self.net_cash or 0)) * 100
  
  @api.one
  def _getMonthlyAmortizationstd(self):
   if self.s_term > 0:
    self.monthly_amortization_std = (((self.amount_financed or 0) * (self.std_bank or 0)) / 100) / (self.s_term)

    logger.info("Total is" + str(self.monthly_amortization_std))

  @api.one
  def _getMonthlyAmortizationoma(self):
   if self.o_term > 0:
    self.monthly_amortization_oma = (((self.amount_financed or 0) * (self.oma_bank or 0)) / 100) / (self.o_term)
    self.oma_oma = (((self.amount_financed or 0) * (self.oma_bank or 0)) / 100) / (self.o_term)

  @api.one
  def _getAmountFinanced(self):
    self.amount_financed = (self.srp or 0) - (self.less_discount or 0) - (self.downpayment or 0) - (self.reservation_fee or 0)

  @api.one
  def _getNCOStd(self):
    self.net_cash_outlay_std = ((self.downpayment or 0) + (self.addons_total or 0) + (self.chattel_mortgage_std or 0) + (self.insurance_std or 0) + (self.lto_registration_std or 0)) - (self.less_total or 0)

  @api.one
  def _getNCOOma(self):
    self.net_cash_outlay_oma = ((self.downpayment or 0) + (self.addons_total or 0) + (self.chattel_mortgage_oma or 0) + (self.insurance_oma or 0) + (self.lto_registration_oma or 0)) - (self.less_total or 0)
  
  @api.multi
  def _getAddonsTotal(self):
    for line in self.addons:
      self.addons_total += line.amount

  @api.multi
  def _getLessTotal(self):
    for line in self.less:
      self.less_total += line.amount_less

  @api.onchange("srp","less_discount","downpayment","net_cash","reservation_fee","amount_financed","oma_bank","o_term","addons_total","chattel_mortgage_oma","chattel_mortgage_std","insurance_oma","insurance_std","lto_registration_oma","lto_registration_std","less_total")
  def unit_change(self):
    self._getNetCash()
    self._getDPPercentage()
    self._getAmountFinanced()
    self._getMonthlyAmortizationoma()
    self._getMonthlyAmortizationstd()
    self._getAddonsTotal()
    self._getNCOOma()
    self._getNCOStd()

  @api.model
  def create(self, vals):
    vals['name'] = self.env['ir.sequence'].next_by_code('fos.calc.seq')
    return super(FOSSaleCalculator, self).create(vals)

FOSSaleCalculator()