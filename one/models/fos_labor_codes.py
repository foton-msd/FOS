from odoo import models, fields, api


class FOSLaborCodes(models.Model):
    _name = "fos.labor.codes"
    _description= "Labor Codes"

    one_local_name_id = fields.Many2one(string="Labor Code", comodel_name='one.local.names')
    product_id = fields.Many2one(string="Code", comodel_name='product.product', required=True,
        domain=[('sub_type','=','labor')])
    description = fields.Text(string="Description", related="product_id.product_tmpl_id.description", readonly=True)
    no_of_hours = fields.Float(string="No of Hours", required=True)
    flat_rate = fields.Float(string="Flat Rate", required=True)

FOSLaborCodes()
