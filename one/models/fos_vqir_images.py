# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class VqirImages(models.Model):
  _name = 'fos.vqir.images'
  _description = 'VQIR - Images'

  name = fields.Char(string="ID", required=True, readonly=True, default='auto-generated')
  fos_vqir_id = fields.Many2one(string="V.Q.I.R.", comodel_name="fos.vqir", required=True)
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
  image_remarks = fields.Text(string="Remarks")

  @api.model
  def create(self, vals):
    vals['name'] = self.env['ir.sequence'].next_by_code('fos.vqir.images.seq')
    result = super(VqirImages, self).create(vals)
    return result


VqirImages()

