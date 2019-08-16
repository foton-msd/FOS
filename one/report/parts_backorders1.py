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
        select e.name as source_code, c.name as part_number, c.description as description, a.product_uom_qty as order_qty,
        a.qty_delivered, (a.product_uom_qty - a.qty_delivered) as backorder,
        f.name as so_number, f.origin as polo_number, f.date_order::date as date_order, g.name as customer_name,
        a.id, a.product_id, f.id as order_id, g.id as partner_id
        from sale_order_line a
        left join product_product b on a.product_id = b.id
        left join product_template c on b.product_tmpl_id = c.id
        left join product_attribute_value_product_product_rel d on d.product_product_id = b.id
        left join product_attribute_value e on d.product_attribute_value_id = e.id
        left join sale_order f on a.order_id = f.id
        left join res_partner g on f.partner_id = g.id
        where c.sub_type = 'parts' and f.state in ('sale','done') and 
            (a.product_uom_qty - a.qty_delivered) > 0;
      """)

PartsBackOrders1()