from odoo import models, fields, api, exceptions, _
import logging
logger = logging.getLogger(__name__)

class FMPIServiceHistory(models.Model):
    _name = "fmpi.service.history"
    _description = "FMPI Performed Services"

    dealer_id = fields.Many2one(string="Dealer", comodel_name="one.dealers")
    name = fields.Char(string="S.O. Number")
    parts_and_jobs = fields.Text(string="Product")
    customer_name = fields.Char(string="Customer Name")
    charged_to = fields.Selection(string="Charged to",
        selection=[('warranty','Warranty'),
        ('customer','Customer'),
        ('internal','Internal'),
        ('add-on-costs','Add-On-Costs')])
    run_km = fields.Integer(string="Run KM")
    one_fu_id = fields.Many2one(string="FOTON Number", comodel_name="view.fas.fu")
    confirmation_date = fields.Datetime(string="Service Date")    
    fmpi_history_id = fields.Integer(string="FMPI History ID")
    
FMPIServiceHistory()