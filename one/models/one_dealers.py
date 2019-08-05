# -*- coding: utf-8 -*-

from odoo import models, fields

class Dealers(models.Model):
  _name = 'one.dealers'
  _description = 'Dealers'

  code = fields.Char(string="Dealer Code", required=False)
  name = fields.Char(string="Dealer Name", required=True)
  reg_name = fields.Char(string="Registered Name")
  street1 = fields.Char(string="Street")
  street2 = fields.Char(string="Street 2")
  city = fields.Char(string="City")
  province = fields.Char(string="Province")
  zip = fields.Char(string="ZIP")
  region = fields.Char(string="Region")
  phone = fields.Char(string="Telephone")
  fax = fields.Char(string="Fax")
  mobile = fields.Char(string="Mobile")
  email = fields.Char(string="Email")
  fmpi_dealer_id = fields.Integer(string="FMPI Dealer ID", readonly=True, invisible=True)
  fmpi_dealer_stamp = fields.Char(string="FMPI Dealer Stamp", readonly=True, invisible=True)
  type = fields.Char(string="Type")
  is_servicing = fields.Boolean(string="Servicing Dealer")
Dealers()
