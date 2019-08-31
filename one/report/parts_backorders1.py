# -*- coding: utf-8 -*- 
from odoo import tools 
from odoo import api, fields, models

class PartsBackOrders1(models.Model):
  _name = 'view.parts.backorders1' 
  _description = 'Parts Backorders'
  _auto = False

  product_id = fields.Many2one(string="Part Number", comodel_name="product.product", readonly=True)
  description = fields.Char(string="Description", readonly=True)
  partner_id = fields.Many2one(string="Customer", comodel_name="res.partner", readonly=True)
  order_id = fields.Many2one(String="S.O. Number", comodel_name="sale.order", readonly=True)
  polo_number = fields.Char(String="POLO Number", readonly=True)
  date_order = fields.Date(string="Order Date", readonly=True)
  source_code = fields.Char(string="SC", readonly=True)
  order_qty = fields.Float(string="Ordered Qty", readonly=True)
  qty_delivered = fields.Float(string="Delivered Qty", readonly=True)
  backorder = fields.Float(string="Unserved Qty", readonly=True)

  @api.model_cr
  def init(self):
    tools.drop_view_if_exists(self.env.cr, "view_parts_backorders1")
    self.env.cr.execute("""
      CREATE OR REPLACE VIEW view_parts_backorders1 AS
      SELECT e.name AS source_code,
        c.name AS part_number,
        c.description,
        a.product_uom_qty AS order_qty,
        a.qty_delivered,
        a.product_uom_qty - a.qty_delivered AS backorder,
        f.name AS so_number,
        f.origin AS polo_number,
        f.date_order::date AS date_order,
        g.name AS customer_name,
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
      WHERE c.sub_type::text = 'parts'::text AND (f.state::text = ANY (ARRAY['sale'::character varying, 'done'::character varying]::text[])) AND (a.product_uom_qty - a.qty_delivered) > 0::numeric
      AND (SELECT COUNT(*) from stock_picking WHERE state != 'done' AND state != 'cancel' AND sale_id = f.id) > 0;
          """)

PartsBackOrders1()