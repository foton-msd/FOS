# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PaymentModes(models.Model):
    _name = 'fos.payment.modes'
    _sql_constraints = [
        ('fos_unique_payment_mode', 'unique(name)','Uniqueness of Payment Modes has been violated!')
    ]
    name = fields.Char(string="Mode of Payment", required=True)

PaymentModes()
