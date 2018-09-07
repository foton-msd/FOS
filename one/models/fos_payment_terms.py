from odoo import models, fields, api

class PaymentTerms(models.Model):
    _name = 'fos.payment.terms'
    _sql_constraints = [
        ('fos_unique_term', 'unique(name)','Uniqueness of Payment Term has been violated!')
    ]
    name = fields.Char(string="Payment Term", required=True)
PaymentTerms()