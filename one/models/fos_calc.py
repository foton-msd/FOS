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
    srp = fields.Float('SRP', digits=dp.get_precision('Product Price'), default=0.0)
    less_discount = fields.Float('Less Discount', default=0.0)
    net_cash = fields.Float(string="Net Cash", compute="_getNetCash", readonly=True)
    downpayment = fields.Float('Downpayment')
    dp_percent = fields.Float('DP (%)', readonly=True)
    amount_financed = fields.Float('Amount Finance', compute="_getAmountFinanced", readonly=True)
    reservation_fee = fields.Float('Reservation Fee')
    bank_id = fields.Many2one(string="Bank", comodel_name="fos.calc.banks")
    s_term = fields.Integer(string="TERM(months)", related="bank_id.standard_term", readonly=True)
    o_term = fields.Integer(string="TERM(months)", related="bank_id.oma_term", readonly=True)
    std_bank = fields.Float(string="Bank Standard", related="bank_id.bank_std")
    oma_bank = fields.Float(string="Bank OMA", related="bank_id.bank_oma")
    monthly_amortization_std = fields.Float('Montly Amortization', compute="_getMonthlyAmortizationstd", readonly=True)
    monthly_amortization_oma = fields.Float('Montly Amortization', compute="_getMonthlyAmortizationoma", readonly=True)
    cash_outlay = fields.Selection(string="Cash Outlay", selection=[('standard', 'Standard'), ('oma', 'OMA')], required=True)
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
    additional_accessories = fields.Float(string="Additional Accessories", compute="_gettotalAccessories", readonly=True)
    net_cash_outlay_std = fields.Float(string="Net Cash Outlay", compute="_getNCOStd", readonly=True)
    net_cash_outlay_oma = fields.Float(string="Net Cash Outlay", compute="_getNCOOma", readonly=True)
    state = fields.Selection(string="Status", selection=[('draft', 'Draft'), ('cancel', 'Cancelled'), ('confirm', 'Confirmed')], default='draft')
    sale_order_id = fields.Many2one(string="Sale Quotation", comodel_name="sale.order", copy=False)
    sale_executive = fields.Many2one(string="Sale Executive", comodel_name="res.users", default=lambda self: self.env.user)
    sale_executive_id = fields.Many2one(string="Sale Executive", comodel_name="fos.sale.executive")
    prepared_by_id = fields.Many2one(string="Prepared by", comodel_name="res.users", default=lambda self: self.env.user)
    prepared_by_desig = fields.Char(string="Designation", related="prepared_by_id.partner_id.function")
    

    @api.one
    def _getNetCash(self):
        self.net_cash = (self.srp or 0) - (self.less_discount or 0)

    @api.one
    def _getMonthlyAmortizationstd(self):
        if self.s_term > 0:
            self.monthly_amortization_std = (
                (self.amount_financed or 0) * (1 + (self.std_bank / 100))) / (self.s_term)

            logger.info("Total is" + str(self.monthly_amortization_std))

    @api.one
    def _getMonthlyAmortizationoma(self):
        if self.o_term > 0:
            self.monthly_amortization_oma = (
                (self.amount_financed or 0) * (1 + (self.oma_bank / 100))) / (self.o_term)
            self.oma_oma = ((self.amount_financed or 0) *
                            (1 + (self.oma_bank / 100))) / (self.o_term)

    @api.one
    def _getAmountFinanced(self):
        self.amount_financed = (self.srp or 0) - (self.less_discount or 0) - \
            (self.downpayment or 0) - (self.reservation_fee or 0)

    @api.one
    def _getNCOStd(self):
        self.net_cash_outlay_std = ((self.downpayment or 0) + (self.addons_total or 0) + (self.chattel_mortgage_std or 0) + (
            self.insurance_std or 0) + (self.lto_registration_std or 0)) - (self.less_total or 0)

    @api.one
    def _getNCOOma(self):
        self.net_cash_outlay_oma = ((self.downpayment or 0) + (self.monthly_amortization_oma) + (self.addons_total or 0) + (
            self.chattel_mortgage_oma or 0) + (self.insurance_oma or 0) + (self.lto_registration_oma or 0)) - (self.less_total or 0)

    @api.multi
    def _getAddonsTotal(self):
        for line in self.addons:
            self.addons_total += line.amount

    @api.multi
    def _gettotalAccessories(self):
        self.additional_accessories = self.addons_total - self.less_total

    @api.multi
    def _getLessTotal(self):
        for line in self.less:
            self.less_total += line.amount_less

    @api.onchange("unit_id")
    def product_changed(self):
        if self.unit_id:
            self.srp = self.unit_id.lst_price

    @api.onchange("srp", "less_discount", "net_cash", "reservation_fee", "amount_financed", "oma_bank", "o_term", "addons_total", "chattel_mortgage_oma", "chattel_mortgage_std", "insurance_oma", "downpayment", "insurance_std", "lto_registration_oma", "lto_registration_std", "less_total")
    def unit_change(self):
        self._getNetCash()
        self._getAmountFinanced()
        self._getMonthlyAmortizationoma()
        self._getMonthlyAmortizationstd()
        self._getAddonsTotal()
        self._getNCOOma()
        self._getNCOStd()

    @api.onchange("downpayment") 
    def DownpaymentChanged(self):   
        if self.srp > 0:
            self.dp_percent = ((self.downpayment or 0) / (self.net_cash or 0)) * 100

    @api.onchange("dp_percent")  
    def DPPercentChanged(self):
        self.downpayment = (self.net_cash) * ((self.dp_percent) * 0.01)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('fos.calc.seq')
        return super(FOSSaleCalculator, self).create(vals)

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def print_sale_calculator(self):
        inet_host = self.env.user.company_id.inet_url
        dbname = self.env.user.company_id.dealer_pgn
        report_url = inet_host + "?report=/" + dbname + \
            "/fos_sales_calculator_quotation.rpt&prompt0=" + str(self.id)
        return {
            'type': 'ir.actions.act_url',
            'url': report_url,
            'target': 'new'
        }

    @api.multi
    def action_confirm(self):
        so_obj = self.env['sale.order']
        self.ensure_one()
        new_so = so_obj.create({
            'partner_id': self.customer_id.id,
            'date_order': fields.datetime.now(),
            'so_type': 'units'})
        if new_so:
            so_line = self.env['sale.order.line']
            # Create unit line
            so_line.create({
                'order_id': new_so.id,
                'charged_to': 'customer',
                'units_and_addons': self.unit_id.id,
                'product_id': self.unit_id.id,
                'product_uom_qty': 1,
                'price_unit': self.srp
            })
            for aol in self.addons:
                so_line.create({
                'order_id': new_so.id,
                'charged_to': 'customer',
                'units_and_addons': aol.product_id.id,
                'product_id': aol.product_id.id,
                'product_uom_qty':1,
                'price_unit': aol.amount  
                })

            for lol in self.less:
                logger.info("Analysing Discount Line: " + str(new_so.id))
                has_addons = False
                so_lines = self.env['sale.order.line'].search([['order_id','=', new_so.id]])
                for sol in so_lines:
                    if sol.product_id.id == lol.product_id.id:
                        logger.info("Discount line found from addons")
                        sol.write({
                            'discount_amount': so_line.discount_amount + lol.amount_less
                        })
                        sol.DiscountAmountChanged()
                        has_addons = True
                        break
                if not has_addons:
                    so_line.create({
                        'order_id': new_so.id,
                        'charged_to': 'customer',
                        'units_and_addons': lol.product_id.id,
                        'product_id': lol.product_id.id,
                        'product_uom_qty':1,
                        'price_unit': lol.amount_less,
                        'discount':100
                    })

        self.write({
            'state': 'confirm',
            'sale_order_id': new_so.id
        })


FOSSaleCalculator()
