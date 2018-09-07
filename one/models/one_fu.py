# -*- coding: utf-8 -*-

from odoo import models, fields

class FotonUnits(models.Model):
  _name = 'one.fu'
  _description = 'FOTON Units from FMPI'

  name = fields.Char(string="FOTON Number", readonly=True)
  description = fields.Char(string="Description", readonly=True)
  engine_number = fields.Char(string="Engine Number", readonly=True)
  chassis_number = fields.Char(string="Chassis Number", readonly=True)
  conduction_sticker = fields.Char(string="Conduction Sticker", readonly=True)
  color = fields.Char(string="Color", readonly=True)
  body_type = fields.Char(string="Body Type", readonly=True)
  year_model = fields.Char(string="Year Model", readonly=True)
  vehicle_type = fields.Char(string="Vehicle Class", readonly=True)
  # LTO Registration info
  plate_number = fields.Char(string="Plate Number")
  cr_number = fields.Char(string="C.R. Number")
  cr_date = fields.Date(string="C.R. Date")
  or_number = fields.Char(string="O.R. Number")
  or_date = fields.Date(string="O.R. Date")
  mv_file_number = fields.Char(string="M.V. File Number")
  owner_name = fields.Char(string="Registered to")
  owner_address = fields.Char(string="Address")
  owner_contact_details = fields.Char(string="Contact Info")
  # FMPI AMS Fields
  fmpi_fu_stamp = fields.Datetime(string="FMPI Unit Stamp", readonly=True)
  fmpi_fu_local_name_id = fields.Many2one(string="Local Name", comodel_name="one.local.names", readonly=True)
  fmpi_dealer_id = fields.Many2one(string="Original Dealer", comodel_name="one.dealers", readonly=True)
  one_dealer_id = fields.Many2one(string="Current Dealer", comodel_name="one.dealers", readonly=True)
  #one_transfer_ids = fields.One2many(string="Transfer Logs", comodel_name="one.fu.transfers", inverse_name="one_fu_id")
  classification = fields.Char(string="Classification", related="fmpi_fu_local_name_id.classification", store=True)
  state = fields.Selection(string="State", selection=[('avail','Available'),('alloc','Allocated'),('sold','Sold')])
  #new_body_type = fields.Char(string="Current Body Type", readonly=True)
  #one_bt_log_ids = fields.One2many(string="Body Type Logs", comodel_name="one.fu.bt.logs", inverse_name="one_fu_id")
  ams_services_ids = fields.One2many(string="Service History", comodel_name="ams.service.records", inverse_name="one_fu_id")
  active_on_dealer = fields.Boolean(string="Active")
  po_line_id = fields.Many2one(string="Order Line", comodel_name="purchase.order.line")
  po_number = fields.Char(string="P.O. Number", related="po_line_id.order_id.name")
  po_amount = fields.Float(string="Unit Cost", related="po_line_id.price_unit")
FotonUnits()
