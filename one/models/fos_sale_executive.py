from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class FOSSaleExecutive(models.Model):
    _name = "fos.sale.executive"
    _description = "Sale Executive"

    name = fields.Char(string="Sale Executive", required=True)

FOSSaleExecutive()