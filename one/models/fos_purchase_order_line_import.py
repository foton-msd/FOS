from xlrd import open_workbook
from odoo import api, models,fields
from odoo.exceptions import UserError
import base64
from odoo import exceptions
import logging
_logger = logging.getLogger(__name__) 

class PurchaseOrderLineImport(models.TransientModel):
  _name='purchase.order.line.import'

  xlsfile = fields.Binary(string="Purchase Order Lines File")
  filename = fields.Char(string="Filename")
  order_id = fields.Many2one(string="PO", comodel_name="purchase.order", required=True, ondelete="cascade")

  @api.multi
  def begin_import(self):
    order_id = self.order_id.id
    wb = open_workbook(file_contents = base64.decodestring(self.xlsfile))
    pp_obj = self.env['product.product']
    po_line_obj = self.env['purchase.order.line']
    vals = []
    for s in wb.sheets():
      for row in range(s.nrows):
        variant_name = s.cell(row,0).value
        product_name = s.cell(row,1).value
        product_description = s.cell(row,2).value or ''
        product_qty = s.cell(row,3).value or 1
        price_unit = s.cell(row,4).value or 0
        p_ids = pp_obj.search([('name', '=', product_name)])
        product_id = 0
        product_uom = 0
        if p_ids:
          if variant_name:
            for pid in p_ids:
              if pid.attribute_value_ids:
                for att in pid.attribute_value_ids:
                  if att.name == variant_name:
                    product_id = pid.id
                    product_uom = pid.uom_id.id
        if product_id:
          #_logger.info("Product ID of "+ product_name + " and Variant "+ variant_name+" is "+ str(order_id))
          vals = {
            'name': product_description,
            'product_qty': product_qty,
            'date_planned': fields.datetime.now(),
            'product_uom': product_uom,
            'product_id': int(product_id),
            'price_unit': price_unit,
            'order_id': int(order_id),            
          }
        if vals:
          _logger.info("Writting values: " + str(vals))
          po_line_obj.create(vals)
PurchaseOrderLineImport()