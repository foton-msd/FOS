# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class FMPIVqirImages(models.Model):
  _name = 'fmpi.vqir.images'
  _description = 'VQIR - Images'

  name = fields.Char(string="ID", required=True, readonly=True, default='auto-generated')
  fmpi_vqir_id = fields.Many2one(string="V.Q.I.R.", comodel_name="fmpi.vqir", readonly=True)
  image_variant = fields.Binary(string="Variant Image", attachment=False,
    help="This field holds the image used as image for the product variant, limited to 1024x1024px.")
  image = fields.Binary("Image", attachment=False,
  	help="This field holds the image used as image for the product, limited to 1024x1024px.")
  image_medium = fields.Binary("Medium-sized image", attachment=False,
	  help="Medium-sized image of the product. It is automatically "
	  "resized as a 128x128px image, with aspect ratio preserved, "
	  "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
  image_small = fields.Binary("Small-sized image", attachment=False,
	  help="Small-sized image of the product. It is automatically "
	  "resized as a 64x64px image, with aspect ratio preserved. "
	  "Use this field anywhere a small image is required.")
  remarks = fields.Text(string="Remarks", readonly=True)

FMPIVqirImages()