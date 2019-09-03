from xlrd import open_workbook
from odoo import api, models,fields
from odoo.exceptions import UserError
import base64
from odoo import exceptions
import logging
logger = logging.getLogger(__name__) 

class PurchaseOrderLineImport(models.TransientModel):
  _name='purchase.order.line.import'

  xlsfile = fields.Binary(string="P.O. Lines File")
  filename = fields.Char(string="Filename")
  order_id = fields.Many2one(string="P.O. Number", comodel_name="purchase.order", required=True, ondelete="cascade")
  line_ids = fields.One2many(string="Order Lines Import", comodel_name="purchase.order.line.line.import", inverse_name="poli_id")
  validated = fields.Boolean(string="Validated", default=False)
  begin_at = fields.Integer(string="Begin import at row", default=6, required=True)
  end_at = fields.Integer(string="End import at row", default=7, required=True)
  sc_col = fields.Selection(string="Source Code", required=True, selection=[
    ('0','A'),('1','B'),('2','C'),('3','D'),('4','E'),('5','F'),('6','G'),('7','H'),('8','I'),
    ('9','J'),('10','K'),('11','L'),('12','M'),('13','N'),('14','O'),('15','P'),('16','Q'),('17','R'),
    ('18','S'),('19','T'),('20','U'),('21','V'),('22','W'),('23','X'),('24','Y'),('25','Z')], default="0")
  pn_col = fields.Selection(string="Part Number", required=True, selection=[
    ('0','A'),('1','B'),('2','C'),('3','D'),('4','E'),('5','F'),('6','G'),('7','H'),('8','I'),
    ('9','J'),('10','K'),('11','L'),('12','M'),('13','N'),('14','O'),('15','P'),('16','Q'),('17','R'),
    ('18','S'),('19','T'),('20','U'),('21','V'),('22','W'),('23','X'),('24','Y'),('25','Z')],default="1")
  desc_col = fields.Selection(string="Description", required=True, selection=[
    ('0','A'),('1','B'),('2','C'),('3','D'),('4','E'),('5','F'),('6','G'),('7','H'),('8','I'),
    ('9','J'),('10','K'),('11','L'),('12','M'),('13','N'),('14','O'),('15','P'),('16','Q'),('17','R'),
    ('18','S'),('19','T'),('20','U'),('21','V'),('22','W'),('23','X'),('24','Y'),('25','Z')],default="2")
  qty_col = fields.Selection(string="Quantity", required=True, selection=[
    ('0','A'),('1','B'),('2','C'),('3','D'),('4','E'),('5','F'),('6','G'),('7','H'),('8','I'),
    ('9','J'),('10','K'),('11','L'),('12','M'),('13','N'),('14','O'),('15','P'),('16','Q'),('17','R'),
    ('18','S'),('19','T'),('20','U'),('21','V'),('22','W'),('23','X'),('24','Y'),('25','Z')],default="3")
  
  validated = fields.Boolean(string="Validated", default=False)

  @api.multi
  def name_get(self):
    result = []
    for event in self:
      result.append((event.id, '%s' % (event.order_id.name)))
    return result

  @api.multi
  def beg_import(self):
    pt_obj = self.env['product.template']
    pp_obj = self.env['product.product']
    for l in self.line_ids:
      if not l.product_id:
        logger.info("Searching/Creating new product template form:" + l.part_number +" (" + l.sc +") "+l.description)
        product_tmpl_id = False
        pt_ids = pt_obj.search([("name","=",l.part_number)],limit=1)
        for pt in pt_ids:
          product_tmpl_id = pt.id
        if not product_tmpl_id:
          # create new
          new_pp = pp_obj.create({
            "name": l.part_number,
            "sub_type": "parts",
            "type": "product",
            "categ_id": 3,
            "description": l.description,
            "description_sale": l.description,
            "description_purchase": l.description,
            "description_pickingin": l.description,
            "description_pickingout": l.description,
            "description_picking": l.description
          })
          if new_pp:
            product_tmpl_id = new_pp.product_tmpl_id
        if product_tmpl_id:
          # create variant
          att_obj = self.env['product.attribute.value'].search([('attribute_id','=',8)])
          value_ids = []
          for att in att_obj:
            value_ids.append(att.id)
          logger.info(str(value_ids))
          new_att = self.env['product.attribute.line'].create({
            'product_tmpl_id': product_tmpl_id.id,
            'attribute_id':8, 
            'value_ids':[[6,0,value_ids]]})
          if new_att:
            p_ids = pp_obj.search([('name', '=', l.part_number)])
            for pid in p_ids:
              if pid.attribute_value_ids:
                for att in pid.attribute_value_ids:
                  if att.name == l.sc:
                    l.write({'product_id': pid.id})
          product_tmpl_id.create_variant_ids()

      # make/update purchase order line
      if l.product_id:
        if l.order_line_id:
          l.order_line_id.write({'product_qty': (l.order_line_id.product_qty or 0) + l.qty})
        else:
          self.env['purchase.order.line'].create({
            'name': l.product_id.description_purchase or l.product_id.name,
            'product_qty': l.qty,
            'date_planned': fields.datetime.now(),
            'product_uom': l.product_id.uom_po_id.id,
            'product_id': int(l.product_id),
            'price_unit': l.product_id.standard_price or 1,
            'order_id': self.order_id.id,            
          })

  @api.multi
  def validate_xls(self):
    order_id = self.order_id.id
    wb = open_workbook(file_contents = base64.decodestring(self.xlsfile))
    pp_obj = self.env['product.product']
    spi_obj = self.env['purchase.order.line.line.import']
    for s in wb.sheets():
      row_num = 0
      for row in range(s.nrows):
        if row_num >= (self.begin_at - 1) and row_num <= (self.end_at - 1):
          variant_name = str(s.cell(row,int(self.sc_col or '0')).value).upper()
          product_name = str(s.cell(row,int(self.pn_col or '0')).value).replace("'","").upper()
          product_description = s.cell(row,int(self.desc_col or '0')).value or ''
          product_qty = s.cell(row,int(self.qty_col or '0')).value or 0
         
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
            logger.info("Part number found. "+product_name+" ID: "+str(product_id))
            # search again on the list
            as_new = True
            for l in self.line_ids:
              if l.product_id.id == product_id:
                as_new = False
                l.write({
                  'qty': (product_qty + l.qty),
                  'note': (l.note or '') + "-- Note: Same part number found. Adding "+str(product_qty or 0)+" to "+str(l.qty or 0)+"\n"})
            if as_new:
              spi_obj.create({
                'poli_id': self.id,
                'product_id': product_id,
                'sc': variant_name,
                'part_number': product_name,
                'description': product_description,
                'qty': product_qty,
              })
              for l2 in self.line_ids:
                for order_line in self.order_id.order_line:
                  if order_line.product_id.id == l2.product_id.id:
                    l2.write({'order_line_id': order_line.id})
          else:
            logger.info(product_name+" not found!")
            # search again on the list
            as_new = True
            for l in self.line_ids:
              if l.part_number == product_name:
                as_new = False
                l.write({
                  'qty': product_qty + l.qty,
                  'note': (l.note or '') + "-- Note: Same part number found. Adding "+str(product_qty)+" to "+str(l.qty)+"\n"})
            if as_new:
              spi_obj.create({
                'poli_id': self.id,
                'sc': variant_name,
                'part_number': product_name,
                'description': product_description,
                'qty': product_qty,
                'note': "-- will create new Parts Master\n"
              })
        row_num += 1
    self.validated = True
    return {"type": "ir.actions.do_nothing",}

PurchaseOrderLineImport()

class PurchaseOrderLineLineImport(models.TransientModel):
  _name='purchase.order.line.line.import'

  poli_id = fields.Many2one(string="Line ID", comodel_name="purchase.order.line.import", readonly=True)
  sc = fields.Char(string="SC", readonly=True)
  part_number = fields.Char(string="Part Number", readonly=True)
  description = fields.Char(string="Description")
  product_id = fields.Many2one(string="FOS Part Number", comodel_name="product.product", readonly=True)
  qty = fields.Integer(string="Quantity", required=True)
  note = fields.Text(string="Actions to execute", readonly=True)
  order_line_id = fields.Many2one(string="Order Line", comodel_name="purchase.order.line")

PurchaseOrderLineLineImport()