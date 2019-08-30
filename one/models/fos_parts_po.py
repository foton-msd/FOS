from xmlrpc import client as xmlrpclib
from odoo.addons import decimal_precision as dp
from odoo import models, fields, api, exceptions, _
import logging
logger = logging.getLogger(__name__)

class FOSPartsPO(models.Model):
    _name = "fos.parts.po"
    _description = "Parts Online Order"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'date desc, id desc'
    _sql_constraints = [
    ('polo_number_unique', 'unique(name)','POLO Number already exists!')]

    name = fields.Char(string="Order Number", readonly=True, default="auto-generated")
    date = fields.Datetime(string="Date", required=True, default=lambda self: fields.datetime.now())
    state = fields.Selection(string="Status", selection=[
        ("draft","Draft"),
        ("cancel","Cancelled"), 
        ("sent","Sent"), 
        ("proc","Processing"),
        ("forpo","Waiting confimation"), 
        ("confirm","Confirmed"),
        ("done","Done")], default="draft")
    notes = fields.Text(string="Notes")
    order_line = fields.One2many(string="Order Line", ondelete="cascade",
        comodel_name="fos.parts.po.line", inverse_name="fos_parts_po_id")
    order_total = fields.Float(string="Order Total without VAT", compute="OrderTotal", 
        digits=dp.get_precision('Product Price'))
    assigned_order_total = fields.Float(string="Served Total without VAT", compute="OrderTotal", 
        digits=dp.get_precision('Product Price'))
    assigned_order_total_with_vat = fields.Float(string="Served Total with VAT", compute="OrderTotal", 
        digits=dp.get_precision('Product Price'))
    order_total_with_vat = fields.Float(string="Order Total with VAT", compute="OrderTotal", 
        digits=dp.get_precision('Product Price'))
    company_id = fields.Many2one('res.company', string='Company',  required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    # data fields used by FMPI
    assigned_product_id = fields.Many2one(string="Part Number", readonly=True, comodel_name="product.product")
    assigned_description = fields.Text(string="Description",readonly=True)
    assigned_order_qty = fields.Float(string="Order Qty", digits=dp.get_precision('Product Unit of Measure'))
    assigned_price_unit = fields.Float(string="Unit Price", readonly=True, digits=dp.get_precision('Product Price'))
    assigned_subtotal = fields.Float(string="Total", readonly=True, compute="LineTotals", digits=dp.get_precision('Product Price'))
    purchase_order_id = fields.Many2one(string="Purchase Order", comodel_name="purchase.order", readonly=True)
    fmpi_parts_so_id = fields.Integer(string="FMPI Parts SO ID", readony=True)

    @api.one
    def action_confirm(self):
        partner_obj = self.env['res.partner']
        partner_id = partner_obj.search([('name','=','UNITED ASIA AUTOMOTIVE GROUP, INC.')]).id
        no_error = True
        if partner_id:
            po_id = self.env['purchase.order'].create({
                'partner_id': partner_id,
                'po_type': 'parts',
                'date_planned': fields.datetime.now(),
                'notes': self.name + "\n" + (self.notes or ""),
                'origin': self.name
            })
            if po_id:
                for line in self.order_line:
                    po_line_id = self.env['purchase.order.line'].create(
                        {
                            'order_id': po_id.id,
                            'fu_id': line.fu_id.id,
                            'product_id': line.assigned_product_id,
                            'name': line.assigned_description,
                            'product_qty': line.order_qty,
                            'price_unit': line.assigned_price_unit,
                            'date_planned': fields.datetime.now(),
                            'product_uom': line.product_id.product_tmpl_id.uom_po_id.id,
                            'eta': line.eta
                        })
                    fpos = po_line_id.order_id.fiscal_position_id
                    po_line_id.taxes_id = fpos.map_tax(po_line_id.product_id.supplier_taxes_id)
                    logger.info("Estimated Time" +str(line.eta))
                    if not po_line_id:
                        no_error = False
            else:
                no_error = False
        else:
            no_error = False   
        if no_error:
            # create sale order to fmpi
            dealer_id = self.company_id.dealer_id.id
            url = self.company_id.fmpi_host.strip()
            db = self.company_id.fmpi_pgn
            username = self.company_id.fmpi_pgu
            password = self.company_id.fmpi_pgp
            # attempt to connect
            logger.info("Connecting to "+url)
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            if not uid:
                raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
                return 
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            # check existence of dealer's name as res_partner from fmpi database
            res_partner_name = self.company_id.dealer_id.name.strip()
            [partner_ids] = models.execute_kw(db, uid, password,
                'res.partner', 'search_read',[[['name','=',res_partner_name]]],
                {'limit':1, 'fields': ['id']})
            #fmpi_partner_id = 0
            if partner_ids:
                fmpi_partner_id = partner_ids['id']
            else:
                fmpi_partner_id = models.execute_kw(db, uid, password, 
                    'res.partner', 'create', [{
                        'name': res_partner_name,
                        'customer': True,
                    }])
            
            if fmpi_partner_id:
                logger.info("Partner ID: " + str(fmpi_partner_id))
                so_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
                    'partner_id': fmpi_partner_id,
                    'so_type': 'parts',
                    'note': self.name + "\n" + (self.notes or ""), 
                    'origin': self.name
                }])
                logger.info("Sale Order ID: " + str(so_id))
                if so_id:
                    line_ids = models.execute_kw(db, uid, password,
                        'fmpi.parts.so.line', 'search_read',[[['fmpi_parts_so_id','=',self.fmpi_parts_so_id]]])
                    if line_ids:
                        for line_id in line_ids:
                            fmpi_parts_so_lines = models.execute_kw(db, uid, password,
                                'fmpi.parts.so.line', 'search_read',[[['id','=',line_id['id']]]])
                            #for line in fmpi_parts_so_lines:
                            values = {
                                'order_id': so_id,
                                'charged_to': 'customer',
                                'part_number': (fmpi_parts_so_lines[0]['assigned_product_id'][0]),
                                'product_id':  (fmpi_parts_so_lines[0]['assigned_product_id'][0]),
                                'name':  (fmpi_parts_so_lines[0]['assigned_description']),
                                'product_uom_qty': (fmpi_parts_so_lines[0]['order_qty']),
                                'price_unit':  (fmpi_parts_so_lines[0]['assigned_price_unit']),
                                'fu_id':  (fmpi_parts_so_lines[0]['fu_id'][0] if fmpi_parts_so_lines[0]['fu_id'] else 0)
                            }
                            models.execute_kw(db, uid, password, 'sale.order.line', 'create', [values])
                            models.execute_kw(db, uid, password, 'fmpi.parts.so', 'write', [[self.fmpi_parts_so_id],{'state':'confirm','sale_order_id': so_id}])
            else:
                raise exceptions.except_orm(_('Remote Action Failed'), _("Cannot create Partner Profile"))
            self.write({'state': 'confirm','purchase_order_id': po_id.id})
            #self.env['purchase.order'].browse([('id','=',po_id.id)]).button_comfirm2()

    @api.one
    def action_send(self):
        dealer_id = self.company_id.dealer_id.id
        # FMPI's API Connection Parameters
        url = self.company_id.fmpi_host.strip()
        db = self.company_id.fmpi_pgn
        username = self.company_id.fmpi_pgu
        password = self.company_id.fmpi_pgp
        # connect to FMPI
        logger.info("Connecting to " + url)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if not uid:
            raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
            return 
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        #fmpi_receipient_ids = models.execute_kw(db, uid, password,
        #    'fmpi.parts.po.email.receipients', 'search_read',[[]],
        #    {'fields': ['name','fullname']})
        #if fmpi_receipient_ids:
        #    for email in fmpi_receipient_ids:
        #        logger.info("Sending email to " + email["name"])     
        # Create record to FMPI's fmpi.parts.so     
        fmpi_parts_so_id = models.execute_kw(db, uid, password, 'fmpi.parts.so', 'create', [{
            'dealer_id': self.company_id.dealer_id.id,
            'name': self.name,
            'date': self.date,
            'state': 'received',
            'notes': self.notes,
            'fos_parts_po_id': self.id,
            'url': self.company_id.dealer_host,
            'db': self.company_id.dealer_pgn,
            'username': self.company_id.dealer_pgu,
            'password': self.company_id.dealer_pgp
            }])
        if fmpi_parts_so_id:
            self.fmpi_parts_so_id = fmpi_parts_so_id
            logger.info("Order ID: " + str(fmpi_parts_so_id))
            for line in self.order_line:
                product_ids = models.execute_kw(db, uid, password,
                    'product.product', 'search_read',[[['product_tmpl_id.name','=',line.product_id.product_tmpl_id.name]]],
                    {'limit':1, 'fields': 'id'})
                if product_ids:
                    for p_id in product_ids:
                        logger.info("Product ID: " + str(p_id['id']))
                        fmpi_parts_so_line_id = models.execute_kw(db, uid, password, 'fmpi.parts.so.line', 
                            'create', [{
                            'fmpi_parts_so_id': fmpi_parts_so_id,
                            'product_id': int(p_id['id']),
                            'description': line.description,
                            'order_qty': line.order_qty,
                            'fu_id': line.fu_id.id,
                            'price_unit': line.price_unit,
                            'vat_amount': line.vat_amount,
                            'subtotal_with_vat': line.subtotal_with_vat,
                            'assigned_product_id': int(p_id['id']),
                            'assigned_description': line.description,
                            'assigned_order_qty': line.order_qty,
                            'assigned_price_unit': line.price_unit,
                            'assigned_vat_amount': line.vat_amount,
                            'assigned_subtotal_with_vat': line.subtotal_with_vat,
                            'fos_parts_po_line_id': line.id,
                            'eta': line.eta
                        }])
        self.write({'state': 'sent'})

    def action_cancel(self):
        if self.state in ["proc","forpo"]:
            dealer_id = self.company_id.dealer_id.id
            url = self.company_id.api_host.strip()
            db = self.company_id.fmpi_pgn
            username = self.company_id.api_user
            password = self.company_id.api_pass
            # attempt to connect
            logger.info("Connecting to "+url)
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            if not uid:
                raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
                return 
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            fmpi_ids = models.execute_kw(db, uid, password,
                    'fmpi.parts.so', 'search_read',[[
                        ['dealer_id','=', dealer_id],
                        ['fos_parts_po_id','=',self.id]
                        ]],
                    {'limit':1, 'fields': 'id'})
            if fmpi_ids:
                for id in fmpi_ids:
                    is_updated = models.execute_kw(db, uid, password, 'fmpi.parts.so', 'write', 
                        [[id['id']], {'state': 'cancel'}])
                if is_updated:
                    self.write({'state': 'cancel'})
        else:
            self.write({'state': 'cancel'})

    @api.one
    def OrderTotal(self):
        ototal = 0
        stotal = 0
        ototalwithvat = 0
        stotalwithvat = 0
        for line in self.order_line:
            ototal += line.subtotal
            stotal += line.assigned_subtotal
            ototalwithvat += line.subtotal_with_vat
            stotalwithvat += line.assigned_subtotal_with_vat
        self.order_total = ototal
        self.assigned_order_total = stotal
        self.order_total_with_vat = ototalwithvat
        self.assigned_order_total_with_vat = stotalwithvat

    @api.model
    def create(self, vals):
        vals['company_id'] = self.env.user.company_id.id
        vals['name'] = self.env['ir.sequence'].next_by_code('fos.parts.po.seq')
        result = super(FOSPartsPO, self).create(vals)
        return result

FOSPartsPO()

class FOSPartsPOLine(models.Model):
    _name = "fos.parts.po.line"
    _description = "Parts Online Order Line"

    fos_parts_po_id = fields.Many2one(string="Order Number", required=True, comodel_name="fos.parts.po", ondelete="cascade")
    state = fields.Selection(string="Status", selection=[
        ("draft","Draft"),
        ("cancel","Cancelled"), 
        ("sent","Sent"), 
        ("proc","Processing"),
        ("forpo","Waiting confimation"), 
        ("confirm","Confirmed"),
        ("done","Done")], related="fos_parts_po_id.state")
    product_id = fields.Many2one(string="Part Number", required=True, comodel_name="product.product")
    sub_type = fields.Selection(string="Sub-Type", related="product_id.product_tmpl_id.sub_type", readonly=True)
    fmpi_product_id = fields.Integer(string="FMPI Product ID")
    fmpi_product = fields.Boolean(string="FMPI Product?", related="product_id.product_tmpl_id.fmpi_product")
    description = fields.Text(string="Description", required=True)
    order_qty = fields.Float(string="Order Qty", required=True, default=1, digits=dp.get_precision('Product Unit of Measure'))
    price_unit = fields.Float(string="Unit Price", digits=dp.get_precision('Product Price'))
    subtotal = fields.Float(string="Total", compute="LineTotals", digits=dp.get_precision('Product Price'))
    fu_id = fields.Many2one(string="FOTON No.", comodel_name="one.fu")
    delivery_date = fields.Date(string="Delivery Date")
    vat_amount = fields.Float(string="VAT Amount", compute='LineTotals')
    subtotal_with_vat = fields.Float(string='Total with VAT', readony=True, compute='LineTotals')
    # data fields used by FMPI
    assigned_product_id = fields.Integer(string="Served-Part Number", readonly=True) 
    assigned_product_name = fields.Char(string="Served-Part Number", readonly=True)
    assigned_description = fields.Text(string="Served-Description", readonly=True)
    assigned_order_qty = fields.Float(string="Served-Qty", digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    assigned_price_unit = fields.Float(string="Served-Unit Price", digits=dp.get_precision('Product Price'), readonly=True)
    assigned_subtotal = fields.Float(string="Served-Total without VAT", compute="LineTotals", digits=dp.get_precision('Product Price'), readonly=True)
    assigned_vat_amount = fields.Float(string="Service-VAT Amount", compute='LineTotals')
    assigned_subtotal_with_vat = fields.Float(string='Serve-Total with VAT', readony=True, compute='LineTotals')
    eta = fields.Datetime(string="ETA", readonly=True)

    @api.one
    def LineTotals(self):
        self.subtotal = self.order_qty * self.price_unit
        self.assigned_subtotal = self.assigned_order_qty * self.assigned_price_unit
        self.vat_amount = self.subtotal * 0.12
        self.subtotal_with_vat = self.vat_amount + self.subtotal
        self.assigned_vat_amount = self.assigned_subtotal * 0.12
        self.assigned_subtotal_with_vat = self.assigned_vat_amount + self.assigned_subtotal

    @api.onchange("product_id", "order_qty")
    def ChangingParts(self):
        dnp = self.product_id.standard_price
        if dnp:
            self.price_unit = dnp
        self.subtotal = self.order_qty * self.price_unit
        self.vat_amount = self.subtotal * 0.12
        self.subtotal_with_vat = self.vat_amount + self.subtotal
        if self.product_id:
            self.description = self.product_id.product_tmpl_id.description
            self.fmpi_product_id = self.product_id.product_tmpl_id.fmpi_product_id




FOSPartsPOLine()

class FMPIOrderPartsEmailReceipients(models.Model):
    _name = "fmpi.parts.po.email.receipients"
    _sql_constraints = [
         ('email_address', 'unique (name)','Email address already existing!')]
    company_id = fields.Many2one('res.company', string='Company',  required=True,
        default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    name = fields.Char(string="Email Address", required=True)
    fullname = fields.Char(string="Full Name")
FMPIOrderPartsEmailReceipients()

class ResCompany(models.Model):
    _inherit = "res.company"
    parts_po_email_receipient_ids = fields.One2many(string="Email Receipients", 
        comodel_name="fmpi.parts.po.email.receipients", inverse_name="company_id")
ResCompany()