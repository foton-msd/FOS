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
    charge_to = fields.Char(string="Charged to")
    run_km = fields.Integer(string="Run KM")
    one_fu_id = fields.Many2one(string="FOTON Number", comodel_name="view.fas.fu")
    service_date = fields.Datetime(string="Service Date")    
FMPIServiceHistory()