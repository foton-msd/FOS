# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BodyTypes(models.Model):
  _name = 'one.body.types'
  _description = 'Body Types'

  name = fields.Char(string="Code", required=True)
  description = fields.Char(string="Description", required=True)
  one_local_name_id = fields.Many2one(string="Local Name", comodel_name="one.local.names")
  fmpi_fu_local_variant_id = fields.Integer(string="FMPI Local Variant ID", readonly=True)
  fmpi_fu_local_variant_stamp = fields.Datetime(string="FMPI Local Variant Stamp", readonly=True)
  image = fields.Binary(
    "Image", attachment=True,
    help="This field holds the image used as image for the product, limited to 1024x1024px.")
  image_medium = fields.Binary(
    "Medium-sized image", attachment=True,
    help="Medium-sized image of the product. It is automatically "
      "resized as a 128x128px image, with aspect ratio preserved, "
      "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
  image_small = fields.Binary(
    "Small-sized image", attachment=True,
    help="Small-sized image of the product. It is automatically "
      "resized as a 64x64px image, with aspect ratio preserved. "
      "Use this field anywhere a small image is required.")

  @api.multi
  def name_get(self):
    result = []
    for event in self:
      result.append((event.id, '[%s] %s' % (event.name, event.description)))
    return result

BodyTypes()
