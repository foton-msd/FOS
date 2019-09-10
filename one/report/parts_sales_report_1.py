# -*- coding: utf-8 -*- 
from odoo import tools 
from odoo import api, fields, models

class PartsSalesReport1(models.Model):
  _name = 'view.parts.sales.report.1' 
  _description = 'Sales Report-1'
  _auto = False

  part_number = fields.Char(string="Part Number", readonly=True)
  description = fields.Char(string="Description", readonly=True)
  confirmation_date = fields.Datetime(string="Confirmation Date", readonly=True)
  customer_name = fields.Char(string="Customer", readonly=True)
  source_code = fields.Char(string="SC", readonly=True)
  so_number = fields.Char(String="S.O. Number", readonly=True)
  polo_number = fields.Char(string="Source Document", readonly=True)
  order_qty = fields.Float(string="Order Qty", readonly=True)
  qty_unserved = fields.Float(string="Unserved Qty", readonly=True)
  qty_delivered = fields.Float(string="Qty Delivered", readonly=True)
  price_unit = fields.Float(string="Unit Price", readonly=True)
  price_total = fields.Float(string="Order Total", readonly=True)
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
      SELECT e.name AS source_code,
        c.name AS part_number,
        c.description,
        a.product_uom_qty AS order_qty,
        a.qty_delivered,
        a.product_uom_qty - a.qty_delivered AS qty_unserved,
        f.name AS so_number,
        f.origin AS polo_number,
        f.confirmation_date,
        g.name AS customer_name,
        a.charged_to,
        a.price_total,
        a.price_unit,
        a.id,
        a.product_id,
        f.id AS order_id,
        g.id AS partner_id
      FROM sale_order_line a
        LEFT JOIN product_product b ON a.product_id = b.id
        LEFT JOIN product_template c ON b.product_tmpl_id = c.id
        LEFT JOIN product_attribute_value_product_product_rel d ON d.product_product_id = b.id
        LEFT JOIN product_attribute_value e ON d.product_attribute_value_id = e.id
        LEFT JOIN sale_order f ON a.order_id = f.id
        LEFT JOIN res_partner g ON f.partner_id = g.id
      WHERE f.state in ('sale','done') AND f.so_type = 'parts';
        """)
PartsSalesReport1()