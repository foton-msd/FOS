from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class FOSSourceOfSale(models.Model):
    _name = "fos.source.of.sale"
    _description = "Source of Sale"

    name = fields.Char(string="Source of Sale", required=True)
    
FOSSourceOfSale()