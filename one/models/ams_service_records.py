from odoo import models, fields, api, exceptions, _
import logging
logger = logging.getLogger(__name__)

class AmsServiceRecord(models.Model):
    _name = "ams.service.records"

    dealer_name = fields.Char(string="Sevicing Dealer")
    customer_name = fields.Char(string="Customer Name")
    run_km = fields.Integer(string="Run KM")
    job_type = fields.Selection(string="Job Type",
        selection=[('major_repair','Major Repair'),
            ('minor_repair','Minor Repair'),
            ('body_repair_insurance','Body Repair Insurance'),
            ('body_repair','Body Repair'),
            ('pms','PMS'),
            ('otc','OTC'),
            ('general_job','General Job'),
            ('warranty','Warranty')])
    one_fu_id = fields.Many2one(string="FOTON Number", comodel_name="one.fu")
    job_product = fields.Char(string="Job/Parts")
    price_unit = fields.Float(string="Unit Price")
    qty_ordered = fields.Float(string="Ordered Qty")
    qty_delivered = fields.Float(string="Delivered Qty")
    qty_invoiced = fields.Float(string="Invoiced Qty")
    price_total = fields.Float(string="Total Price")
    charged_to = fields.Selection(string="Charged to", required=True,
        selection=[('warranty','Warranty'),
            ('customer','Customer'),
            ('internal','Internal'),
            ('add-on-costs','Add-On-Costs')])
    one_charged_to = fields.Selection(string="Charged to", 
        selection=[('warranty','Warranty'),
            ('customer','Customer'),
            ('internal','internal')])   
    order_line_id = fields.Integer(string="Order Line ID") 