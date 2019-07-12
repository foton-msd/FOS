from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class ServiceTechnician(models.Model):
    _name = "fos.service.technician"
    _description = "Service Technician"
    _sql_constraints = [
         ('Unique_sTechnician_Name', 'unique (name)','Technician Name already existing!')]
    name = fields.Char(string='Full Name', required=True)
    active = fields.Boolean(string="Active", default=True)
    order_line_id = fields.Many2one(string="Sale Order Line", comodel_name="sale.order.line")

ServiceTechnician()

