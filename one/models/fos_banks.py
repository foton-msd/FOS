# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Banks(models.Model):
    _name = 'fos.banks'
    _sql_constraints = [
        ('fos_unique_bank', 'unique(name)','Uniqueness of Bank Names has been violated!')
    ]
    name = fields.Char(string="Bank", required=True)

Banks()
