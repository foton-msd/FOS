# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FOSCalcUnitPrices(models.Model):
    _inherit = 'product.product'

    insurance_std = fields.Float(string="Insurance")
    chattel_mortgage_std = fields.Float(string="Chattel Mortgage")
    lto_registration_std = fields.Float(string="LTO Registration")
    insurance_oma = fields.Float(string="Insurance")
    chattel_mortgage_oma = fields.Float(string="Chattel Mortgage")
    lto_registration_oma = fields.Float(string="LTO Registration")

FOSCalcUnitPrices()