from odoo import models, fields, api, tools
import logging

class FOSSerial(models.Model):
    _inherit = 'stock.production.lot'
    _sql_constraints = [
         ('foton_unit', 'unique (fos_fu_id)','FOTON Number already assigned!')]

    fos_fu_id = fields.Many2one(string="FOTON Number", comodel_name="view.fas.fu", required=True)

FOSSerial()