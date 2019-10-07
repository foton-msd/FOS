# -*- coding: utf-8 -*- 
from odoo import tools 
from odoo import api, fields, models

class fosDSSR(models.Model):
  _name = 'view.fos.dssr.1' 
  _description = 'DSSR-1'
  _auto = False

  sale_order_id = fields.Many2one(string="Repair Estimate", comodel_name="sale.order")
  partner_id = fields.Many2one(string="Customer", comodel_name="res.partner")
  fu_id = fields.Many2one(string="FOTON Numner", comodel_name="one.fu")
  product_id = fields.Many2one(string="Product", comodel_name="product.product")
  fos_job_type_id = fields.Many2one(string="Scope of Work", comodel_name="fos.job.type")
  repair_order_id = fields.Many2one(string="Repair Order", comodel_name="fos.repair.orders")

  run_km = fields.Integer(string="Run KM", related="sale_order_id.run_km")
  pn_lc = fields.Char(string="Parts and Labor", related="product_id.product_tmpl_id.name")
  description = fields.Char(string="Description")
  plate_number = fields.Char(string="Plate Number", related="fu_id.plate_number")
  repair_order_date = fields.Datetime(string="Date", related="repair_order_id.date")
  one_local_name_id = fields.Many2one(string="Model", comodel_name="one.local.names")

  @api.model_cr
  def init(self):
    tools.drop_view_if_exists(self.env.cr, "view_fos_dssr_1")
    self.env.cr.execute("""
      CREATE OR REPLACE VIEW view_fos_dssr_1 AS
      SELECT 
        a.id,
        a.name AS description,
        a.order_id AS sale_order_id,
        b.partner_id,
        b.fu_id,
        a.product_id,
        c.id as repair_order_id,
        b.fos_job_type_id,
        d.fmpi_fu_local_name_id AS one_local_name_id
      FROM sale_order_line a
      LEFT JOIN sale_order b ON a.order_id = b.id
      LEFT JOIN fos_repair_orders c ON b.id = c.estimate_id
      LEFT JOIN one_fu d ON b.fu_id = d.id
      WHERE b.so_type = 'service'::text AND b.state NOT IN ('sale'::text, 'cancel'::text);
    """)

fosDSSR()