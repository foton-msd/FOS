from xmlrpc import client as xmlrpclib
from odoo.addons import decimal_precision as dp
from odoo import models, fields, api, exceptions, _
import logging
logger = logging.getLogger(__name__)

class FMPIPartsSO(models.Model):
    _name = "fmpi.parts.so"
    _description = "Parts Online Order"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'date desc, id desc'

    dealer_id = fields.Many2one(string="Dealer ID", comodel_name="one.dealers", readonly=True)
    name = fields.Char(string="Order Number", readonly=True)
    date = fields.Datetime(string="Date Order")
    date_received = fields.Datetime(string="Date Received", required=True, default=lambda self: fields.datetime.now())
    state = fields.Selection(string="Status", selection=[
        ("received","Received"), 
        ("proc","Processing"), 
        ("forpo","Waiting confimation"), 
        ('confirm','Confirmed'), 
        ("cancel","Cancelled"),
        ("done","Done")
        ], default='received')
    notes = fields.Text(string="Notes")
    order_line = fields.One2many(string="Order Line", ondelete="cascade",
        comodel_name="fmpi.parts.so.line", inverse_name="fmpi_parts_so_id")
    order_total = fields.Float(string="Order Total", compute="OrderTotal", 
        digits=dp.get_precision('Product Price'))
    assigned_order_total = fields.Float(string="Served Total", compute="OrderTotal", 
        digits=dp.get_precision('Product Price'))
    company_id = fields.Many2one('res.company', string='Company',  required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    url = fields.Char(string="URL", readonly=True, required=True)
    db = fields.Char(string="Database", readonly=True, required=True)
    username = fields.Char(string="User Name", readonly=True, required=True)
    password = fields.Char(string="Password", readonly=True, required=True)
    fos_parts_po_id = fields.Integer(string="PO Number", readonly=True, required=True)
        
    @api.one
    def OrderTotal(self):
        ototal = 0
        stotal = 0
        for line in self.order_line:
            ototal += line.subtotal
            stotal += line.assigned_subtotal
        self.order_total = ototal
        self.assigned_order_total = stotal
 
    @api.one
    def action_proc(self):
        fos_parts_po_id = self.fos_parts_po_id
        db = self.db
        url = self.url
        username = self.username
        password = self.password
        # attempt to connect
        logger.info("Connecting to "+url)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if not uid:
            raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
            return
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        if models:
            logger.info("Models: " + str(models))
            mod_out = models.execute_kw(db, uid, password, 'fos.parts.po', 'write', 
                [[self.fos_parts_po_id,], {'state': 'proc'}])
            #if mod_out:
            #    logger.info("Mod_Out:" + str(mod_out))
            #    for line in self.order_line:
            #        logger.info("Product ID:" + str(line.assigned_product_id.id))
            #        is_updated = models.execute_kw(db, uid, password, 'fos.parts.po.line', 'write', 
            #            [[line.fos_parts_po_line_id,], 
            #            {
            #                'assigned_product_id': line.assigned_product_id.id,
            #                'assigned_product_name': line.assigned_product_name,
            #                'assigned_description': line.assigned_description,
            #                'assigned_order_qty': line.assigned_order_qty,
            #                'assigned_price_unit': line.assigned_price_unit
            #            }])
            self.write({'state': 'proc'})

    @api.one
    def action_forpo(self):
        fos_parts_po_id = self.fos_parts_po_id
        db = self.db
        url = self.url
        username = self.username
        password = self.password
        # attempt to connect
        logger.info("Connecting to "+url)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if not uid:
            raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
            return
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        if models:
            logger.info("Models: " + str(models))
            mod_out = models.execute_kw(db, uid, password, 'fos.parts.po', 'write', 
                [[fos_parts_po_id,], {'state': 'forpo'}])
            if mod_out:
                # search dealer's parts existence
                for line in self.order_line:
                    name_template = line.assigned_product_id.product_tmpl_id.name
                    dealer_pt = models.execute_kw(db, uid, password,
                        'product.product', 'search_read',[[['name','=',name_template]]])
                    if not dealer_pt:
                        raise exceptions.except_orm(_('Remote Search Failed'), _(name_template + " does not exists on Dealer's Parts Master"))
                    else:
                        logger.info("Product ID:" + str(line.assigned_product_id.id))
                        is_updated = models.execute_kw(db, uid, password, 'fos.parts.po.line', 'write', 
                            [[line.fos_parts_po_line_id,], 
                            {
                                'assigned_product_id': dealer_pt[0]['id'],
                                'assigned_product_name': line.assigned_product_name,
                                'assigned_description': line.assigned_description,
                                'assigned_order_qty': line.assigned_order_qty,
                                'assigned_price_unit': line.assigned_price_unit,
                                'eta': line.eta
                            }])
                self.write({'state': 'forpo'})

            
    #@api.one
    #def action_forpo(self):
    #    fos_parts_po_id = self.fos_parts_po_id
    #    db = self.db
    #    url = self.url
    #    username = self.username
    #    password = self.password
    #    # attempt to connect
    #    logger.info("Connecting to "+url)
    #    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    #    uid = common.authenticate(db, username, password, {})
    #    if not uid:
    #        raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
    #        return
    #    #logger.info("FOS Parts Order ID:" + str([fos_parts_po_id]))
    #    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    #    if models:
    #        is_updated = models.execute_kw(db, uid, password, 'fos.parts.po', 'write', 
    #            [[fos_parts_po_id,], {'state': 'forpo'}])
    #        
    #        if is_updated:
    #            self.write({'state': 'forpo'})
FMPIPartsSO()    

class FMPIPartsSOLine(models.Model):
    _name = "fmpi.parts.so.line"
    _description = "Parts Online Order Line"

    fmpi_parts_so_id = fields.Many2one(string="Order Number", required=True, 
        comodel_name="fmpi.parts.so", ondelete="cascade")
    state = fields.Selection(string="Status", selection=[
        ("received","Received"), 
        ("proc","Processing"), 
        ("forpo","Waiting confimation"), 
        ('confirm','Confirmed'), 
        ("cancel","Cancelled"),
        ("done","Done")
        ], related="fmpi_parts_so_id.state")
    # data fields from dealer's purchase order
    fu_id = fields.Many2one(string="FOTON No.", comodel_name="one.fu", readonly=True)
    product_id = fields.Many2one(string="Order-Part Number", readonly=True, comodel_name="product.product")
    description = fields.Text(string="Order-Description", readonly=True)
    order_qty = fields.Float(string="Order-Qty", readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    price_unit = fields.Float(string="Order-Unit Price", readonly=True, digits=dp.get_precision('Product Price'))
    subtotal = fields.Float(string="Order-Total", compute="LineTotals", digits=dp.get_precision('Product Price'))
    # data fields used by FMPI
    assigned_product_id = fields.Many2one(string="Served-Part Number", comodel_name="product.product")
    assigned_product_name = fields.Char(string="Part Number", related="assigned_product_id.product_tmpl_id.name")
    assigned_description = fields.Text(string="Served-Description")
    assigned_order_qty = fields.Float(string="Served-Qty", digits=dp.get_precision('Product Unit of Measure'))
    assigned_price_unit = fields.Float(string="Served-Unit Price", readonly=True, digits=dp.get_precision('Product Price'))
    assigned_subtotal = fields.Float(string="Served-Total", compute="LineTotals", digits=dp.get_precision('Product Price'))
    fos_parts_po_line_id = fields.Integer(string="FOS Parts PO Line ID") 
    eta = fields.Datetime(string="ETA", default=fields.Datetime.now)
    received_qty = fields.Float(string="Received Qty")
    
    @api.one
    def LineTotals(self):
        self.subtotal = self.order_qty * self.price_unit
        self.assigned_subtotal = self.assigned_order_qty * self.assigned_price_unit
    
    @api.onchange("assigned_product_id", "assigned_order_qty", "assigned_sub_total")
    def ChangingAssignedParts(self):
        dnp = self.assigned_product_id.list_price
        #if dnp:
        self.assigned_price_unit = dnp or 0
        self.assigned_subtotal = self.assigned_order_qty * self.assigned_price_unit
        if self.assigned_product_id:
            self.assigned_description = self.assigned_product_id.product_tmpl_id.description
            logger.info("Changing Served...")
    
    
FMPIPartsSOLine()