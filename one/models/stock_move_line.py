from odoo import models, fields, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    description = fields.Text(string="Description", related="product_id.product_tmpl_id.description")

StockMoveLine()

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    description = fields.Text(string="Description", compute="getDescription")

    @api.multi    
    def getDescription(self):        
        description = ""
        for row in self:
            if row.product_id.product_tmpl_id.description:
                description = row.product_id.product_tmpl_id.description
            elif row.product_id.product_tmpl_id.description_sale:
                description = row.product_id.product_tmpl_id.description_sale
            elif row.product_id.product_tmpl_id.description_purchase:
                description = row.product_id.product_tmpl_id.description_purchase
            elif row.product_id.product_tmpl_id.description_picking:
                description = row.product_id.product_tmpl_id.description_picking
            elif row.product_id.product_tmpl_id.description_pickingin:
                description = row.product_id.product_tmpl_id.description_pickingin
            elif row.product_id.product_tmpl_id.description_pickingout:
                description = row.product_id.product_tmpl_id.description_pickingout
            row.description = description

StockMove()