from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class FOSProductivityLosses(models.Model):
    _name = "fos.productivity.losses"
    _description = "Productivity Losses"

    name = fields.Char(string='Reason', required=True)
    loss_type = fields.Selection(string="Effectiveness", selection=[
        ('availability', 'Availability'),
        ('performance', 'Performance'),
        ('quality', 'Quality'),
        ('productive', 'Productive')])
    manual = fields.Boolean(string='Is a blocking Reason')

FOSProductivityLosses()
