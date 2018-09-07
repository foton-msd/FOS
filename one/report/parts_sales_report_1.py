# -*- coding: utf-8 -*- 
from odoo import tools 
from odoo import api, fields, models

class PartsSalesReport1(models.Model):
  _name = 'view.parts.sales.report.1' 
  _description = 'Sales Report-1'
  _auto = False

  product_id = fields.Many2one(string="Part Number", comodel_name="product.product")
  name = fields.Char(string="Part Number", related="product_id.product_tmpl_id.name")
  confirmation_date = fields.Datetime(string="Confirmation Date")
  partner_id = fields.Many2one(string="Customer", comodel_name="res.partner")
  order_id = fields.Many2one(String="S.O. Number", comodel_name="sale.order")
  product_uom_qty = fields.Float(string="Order Qty")
  price_unit = fields.Float(string="Unit Price")
  price_subtotal = fields.Float(string="Order Total")
  charged_to = fields.Selection(string="Charged to", required=True,
    selection=[('warranty','Warranty'),
      ('customer','Customer'),
      ('internal','Internal'),
      ('add-on-costs','Add-On-Costs')])

  @api.model_cr
  def init(self):
    tools.drop_view_if_exists(self.env.cr, "view_parts_sales_report_1")
    self.env.cr.execute("""
      CREATE OR REPLACE VIEW view_parts_sales_report_1 AS
        SELECT a.*, b.partner_id, b.confirmation_date, b.sq_number, b.name AS so_number 
        FROM sale_order_line a
        LEFT JOIN sale_order b ON a.order_id = b.id
        WHERE b.state in ('sale','done') AND b.so_type = 'parts'
        """)

PartsSalesReport1()