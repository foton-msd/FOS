from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class FOSSourceOfAwareness(models.Model):
    _name = "fos.source.of.awareness"
    _description = "Source of Awareness"

    name = fields.Char(string="Source of Awareness", required=True)
    
FOSSourceOfAwareness()