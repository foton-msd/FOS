from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class FOSSaleExecutive(models.Model):
    _name = "fos.sale.executive"
    _description = "Sale Executive"
    _sql_constraints = [
         ('Unique_SE_Name', 'unique (name)','Sales Executive already exist!')]
    name = fields.Char(string='Full Name', required=True)
    active = fields.Boolean(string="Active", default=True)

FOSSaleExecutive()