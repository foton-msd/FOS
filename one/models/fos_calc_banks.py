# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FOSSaleCalculatorBanks(models.Model):
    _name = 'fos.calc.banks'

    name = fields.Char(string="Bank", required=True)
    standard_term = fields.Integer(string="Standard Term(months)")
    oma_term = fields.Integer(string="OMA Term(months)")
    bank_std = fields.Float(string="Bank Standard (%)")
    bank_oma = fields.Float(string="Bank OMA (%)")    
    

FOSSaleCalculatorBanks()