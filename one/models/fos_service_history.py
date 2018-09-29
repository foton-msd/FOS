from odoo import models, fields, api, exceptions, _
import logging
logger = logging.getLogger(__name__)

class FosServiceHistory(models.Model):
    _name = "fos.service.history"
    _description = "Dealer's Performed Services"

    name = fields.Many2one(string="S.O. Number", comodel_name="sale.order.line")
    parts_and_jobs = fields.Text(string="Product", related="name.name")
    customer_id = fields.Many2one(string="Customer Name", comodel_name="res.partner")
    charge_to = fields.Char(string="Charged to")
    run_km = fields.Integer(string="Run KM")
    one_fu_id = fields.Many2one(string="FOTON Number", comodel_name="view.fas.fu")    
    service_date = fields.Datetime(string="Service Date", related="name.order_id.confirmation_date")
    posted = fields.Boolean(string="Posted")
FosServiceHistory()