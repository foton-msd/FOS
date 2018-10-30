# -*- coding: utf-8 -*-
from xmlrpc import client as xmlrpclib
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError
from odoo import models, fields, api, exceptions, _
import logging
logger = logging.getLogger(__name__)

class FasSaleOrder(models.Model):
  _inherit = 'sale.order'
  
  so_type = fields.Selection(string="Order Type", required=True, readonly=True, states={'draft': [('readonly', False)]},
    selection=[('units','Units'),('parts','Parts'),('service','Service'),('service2','Service-NF'),('addoncost','Add-on Cost')])
  run_km = fields.Integer(string="Run KM")
  fas_area_id = fields.Many2one(string="Area", comodel_name="fas.area")
  fos_job_type_id = fields.Many2one(string="Job Type", comodel_name="fos.job.type")
#  job_type = fields.Selection(string="Job Type",
#    selection=[('major_repair','Major Repair'),
#      ('minor_repair','Minor Repair'),
#      ('body_repair_insurance','Body Repair Insurance'),
#      ('body_repair','Body Repair'),
#      ('pms','PMS'),
#      ('otc','OTC'),
#      ('general_job','General Job'),
#      ('warranty','Warranty')])
  prepared_by_id = fields.Many2one(string="Prepared by", comodel_name="res.users", default=lambda self: self.env.user, readonly=True)
  prepared_by_desig = fields.Char(string="Designation", related="prepared_by_id.partner_id.function", readonly=True)
  checked_by = fields.Char(string="Checked by")
  approved_by = fields.Char(string="Approved by")
  checked_by_desig = fields.Char(string="Designation")
  
  approved_by_desig = fields.Char(string="Designation")
  sq_number = fields.Char(string="Quotation Number", readonly=True)
  # unit info fields for service
  fu_id = fields.Many2one(string="FOTON Number", comodel_name="one.fu")
  fu_chassis_number = fields.Char(string="Chassis Number", related="fu_id.chassis_number", readonly=True)
  fu_engine_number = fields.Char(string="Engine Number", related="fu_id.engine_number", readonly=True)
  fu_conduction_sticker = fields.Char(string="Conduction Sticker", related="fu_id.conduction_sticker", readonly=True)
  fu_plate_number = fields.Char(string="Plate Number", related="fu_id.plate_number", readonly=True)
  fu_color = fields.Char(string="Color", related="fu_id.color", readonly=True)
  fu_local_name_id = fields.Many2one(string="Local Name", related="fu_id.fmpi_fu_local_name_id", comodel_name="one.local.names", readonly=True)
  fu_body_type = fields.Char(string="Body Type", related="fu_id.body_type", readonly=True)
  # unit info fields for sales
  su_fu_id = fields.Many2one(string="FOTON Number", comodel_name="view.fas.fu", domain=[('state','=','avail')])
  su_fu_chassis_number = fields.Char(string="Chassis Number", related="su_fu_id.chassis_number", readonly=True)
  su_fu_engine_number = fields.Char(string="Engine Number", related="su_fu_id.engine_number", readonly=True)
  su_fu_conduction_sticker = fields.Char(string="Conduction Sticker", related="su_fu_id.conduction_sticker", readonly=True)
  su_fu_plate_number = fields.Char(string="Plate Number", related="su_fu_id.plate_number", readonly=True)
  su_fu_color = fields.Char(string="Color", related="su_fu_id.color", readonly=True)
  su_fu_local_name_id = fields.Many2one(string="Local Name", related="su_fu_id.fmpi_fu_local_name_id", comodel_name="one.local.names", readonly=True)
  # unit info fields for non-foton service
  nonf_unit_id = fields.Many2one(string="Plate Number", comodel_name="nonf.units")
  nonf_chassis_number = fields.Char(string="Chassis Number", related="nonf_unit_id.chassis_number", readonly=True)
  nonf_engine_number = fields.Char(string="Engine Number", related="nonf_unit_id.engine_number", readonly=True)
  nonf_conduction_sticker = fields.Char(string="Conduction Sticker", related="nonf_unit_id.conduction_sticker", readonly=True)
  nonf_plate_number = fields.Char(string="Plate Number", related="nonf_unit_id.name", readonly=True)
  nonf_color = fields.Char(string="Color", related="nonf_unit_id.color", readonly=True)
  nonf_maker = fields.Char(string="Make", related="nonf_unit_id.maker_id.name", readonly=True)
  nonf_model = fields.Char(string="Model", related="nonf_unit_id.model_id.name", readonly=True)
  #
  repair_order_id = fields.Many2one(string="Repair Order", comodel_name="fos.repair.orders", copy=False)
  fos_payment_term_id = fields.Many2one(string="Payment Term", comodel_name="fos.payment.terms")
  fos_bank_id = fields.Many2one(string="Bank", comodel_name="fos.banks")
  fos_payment_mode_id = fields.Many2one(string="Mode of Payment", comodel_name="fos.payment.modes")
  payment_mode_name = fields.Char(string="Payment Mode Name", related="fos_payment_mode_id.name", readonly=True)
  unit_si_amount = fields.Float(string="S.I. Amount", readonly=True, compute="getInvoiceAmount")
  unit_si_date = fields.Date(string="S.I. Date", readonly=True)
  date_released = fields.Date(string="Date Released", readonly=True)
  dp_percentage = fields.Float(string="D/P (%)")
  dp_amount = fields.Float(string="D/P (amount)")
  af = fields.Float(string="AF")
  insurance_company = fields.Char(string="Insurance Company")
  source_of_awareness = fields.Char(string="Source of awareness")
  source_of_sale = fields.Char(string="Source of sale")
  venue_of_marketing_activity = fields.Char(string="Venue of Marketing Activity")
  promo = fields.Selection(string="Promo", selection=[
    ('1','Zero Interest'),
    ('2','Low DP'),
    ('3','All-in'),
    ('4','Low DP and All-in'),
    ('5','Low Montly'),
    ('6','Zero Interest and Low Monthly'),
    ('7','Promo Rate')])
  product_total = fields.Float(string="Product Total", compute="getProductTotal", readonly=True)
  labor_total = fields.Float(string="Labor Total", compute="getLaborTotal", readonly=True)
  parts_total = fields.Float(string="Parts Total", compute="getPartsTotal", readonly=True)
  nonf_ro_id = fields.Many2one(string="Repair Order", comodel_name="nonf.ro", copy=False)
  nonf_unit_id = fields.Many2one(string="Non-FOTON Units", comodel_name="nonf.units", copy=False)
  
  @api.model
  @api.multi
  def getInvoiceAmount(self):
    si_amount = 0
    if self.so_type == 'units':
      for l in self.order_line:
        si_amount += l.amt_invoiced
    self.unit_si_amount = si_amount

  @api.multi  
  def action_cancel2(self):
    return self.write({'state': 'cancel'})

  @api.multi
  def action_confirm2(self):
    validated = True  
    seq = ''  
    if self.so_type == 'service':
      # removed as per request of Angela Navarro 09/24/2018 by Jun Salinga
      # validated = self.check_limit()
      seq = 'fos.svso.seq'
    elif self.so_type == 'parts':
      validated = self.check_limit()
      seq = 'fos.spso.seq'
    elif self.so_type == "units":
      seq = 'fos.suso.seq'
    elif self.so_type == "service2":
      seq = 'nonf.svso.seq'
    if validated:
      self.write({
          'sq_number': self.name,
          'name': self.env['ir.sequence'].next_by_code(seq)})
      self._action_confirm()
      if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
        self.action_done()
      if self.so_type == 'units' and self.su_fu_id:        
        self.env.cr.execute(""" UPDATE one_fu SET state = 'alloc' WHERE id = %s""" %(self.su_fu_id.id))
        
      if self.so_type == 'service':
        vqir_obj = self.env['fos.vqir']
        has_warranty_line = False
        for line in self.order_line:
          if line.charged_to == "warranty":
            has_warranty_line = True
            break
        if has_warranty_line:
          new_vqir_id = vqir_obj.create({
            'vqir_type': 'warranty',
            'vqir_date': datetime.today(),
            'date_occur': datetime.today(),
            'fos_fu_id': self.fu_id.id,
            'ss_name': self.company_id.name,
            'ss_street1': self.company_id.street,
            'ss_street2': self.company_id.street2,
            'ss_city': self.company_id.city,
            'ss_phone': self.company_id.phone,
            'ss_email': self.company_id.email,
            'users_name': self.partner_id.name,
            'users_street1': self.partner_id.street,
            'users_mobile': self.partner_id.mobile,
            'users_phone': self.partner_id.phone,
            'run_km': self.run_km,
            'company_id': self.company_id.id
            })
          if new_vqir_id:
            pj_obj = self.env['fos.vqir.parts.and.jobs']
            for line in self.order_line:
              if line.charged_to == "warranty":
                if line.product_id.type == "product":
                  pj_obj.create({
                    'fos_vqir_id': new_vqir_id.id,
                    'parts_number': line.product_id.name,
                    'parts_desc': line.name,
                    'parts_qty': line.product_uom_qty,
                    'parts_cost': line.price_unit
                  })
                else:
                  pj_obj.create({
                    'fos_vqir_id': new_vqir_id.id,
                    'job_code': line.product_id.name,
                    'job_code_desc': line.name,
                    'job_qty': line.product_uom_qty,
                    'job_cost': line.price_unit
                  })
      
    return True
  
  @api.multi
  @api.model
  def action_confirm(self, a_value):
    if self.so_type == "units":
      lines = self.order_line
      if lines:
        for line in lines:
          if line.fu_id.product_id.id == line.product_id.id:
            fu_id = line.fu_id
            fu_state = fu_id.state
            fu_active = fu_id.active
            logger.info("Checking status of FOTON Number: " +fu_id.name)
            if not fu_active:
              raise exceptions.except_orm(_('Inactive Units'),_("FOTON Number: "+ fu_id.name + " is already deactivated!"))
            else:
              if fu_state != "avail":
                raise exceptions.except_orm(_('Already Allocated/Sold'), 
                  _("FOTON Number: " + fu_id.name + " is already allocated/sold to " + 
                  self.partner_id.name + " (" + self.name +")" ))
              else:
                fu_obj = self.pool.get("fas.fu")
                if fu_obj:
                  isConfirmed = super(FasSaleOrder,self).action_confirm()
                  if isConfirmed:
                    fu_obj.write(line.fu_id, {'state': 'alloc', 'so_line_id': line.id})
                  else:
                    logger.info("NO Order Lines found!")
                else:
                  super(FasSaleOrder,self).action_confirm()
    else:
      super(FasSaleOrder,self).action_confirm()

  @api.multi
  def check_limit(self):
    logger.info("Checking credit limits...")
    retval = True
    """Check if credit limit for partner was exceeded."""
    self.ensure_one()
    partner = self.partner_id
    moveline_obj = self.env['account.move.line']
    movelines = moveline_obj.\
      search([('partner_id', '=', partner.id),
              ('account_id.user_type_id.type', 'in',
              ['receivable', 'payable']),
              ('full_reconcile_id', '=', False)])

    debit, credit = 0.0, 0.0
    today_dt = datetime.strftime(datetime.now().date(), DF)
    for line in movelines:
      if line.date_maturity < today_dt:
        credit += line.debit
        debit += line.credit
    logger.info("Creadit Limit:" + str(((credit or 0) - (debit or 0) + self.amount_total) ))
    if ((credit or 0) - (debit or 0) + self.amount_total) > partner.credit_limit:
      # Consider partners who are under a company.
      if partner.over_credit or (partner.parent_id and partner.parent_id.over_credit):
        partner.write({'credit_limit': credit - debit + self.amount_total})
        retval = True
      else:
        msg = '''%s Cannot confirm Sale Order\n\nTotal mature due Amount
          %s as on %s \n\nCheck Partner Accounts or Credit Limits !''' % (partner.name, credit - debit, today_dt)
        raise UserError(_('Credit Over Limits !\n' + msg))

    return retval

  @api.multi
  def getLaborTotal(self):
    for line in self.order_line:
      if line.product_id.type == "service":
        self.labor_total += line.price_total

  @api.multi
  def getPartsTotal(self):
    for line in self.order_line:
      if line.product_id.type == "product":
        self.parts_total += line.price_total

  @api.multi
  def print_saleorder_service(self):
    return self.env.ref('one.report_service_saleorder').report_action(self)

  @api.multi
  def print_so_nfservice(self):
    return self.env.ref('one.report_so_nonf_service').report_action(self)

  @api.multi
  def print_saleorder_parts(self):
    return self.env.ref('one.report_parts_saleorder').report_action(self)

  @api.multi
  def print_so_parts(self):
    return self.env.ref('one.report_so_parts').report_action(self)

  @api.multi
  def print_so_parts_quote(self):
    return self.env.ref('one.report_so_parts_quote').report_action(self)

  @api.multi
  def print_so_units(self):
    return self.env.ref('one.report_so_units').report_action(self)  

  @api.multi
  def print_so_service(self):
    return self.env.ref('one.report_so_service').report_action(self)  
  
  @api.multi
  def print_so_service_quote(self):
    return self.env.ref('one.report_so_service_quote').report_action(self) 

  @api.model
  def create(self, vals):
    if vals['so_type'] == "parts":
      vals['name'] = self.env['ir.sequence'].next_by_code('fos.spsq.seq')
    elif vals['so_type'] == "service":
      vals['name'] = self.env['ir.sequence'].next_by_code('fos.svre.seq')
    elif vals['so_type'] == "units":
      vals['name'] = self.env['ir.sequence'].next_by_code('fos.susq.seq')
    elif vals['so_type'] == "service2":
      vals['name'] = self.env['ir.sequence'].next_by_code('nonf.nfre.seq')
    return super(FasSaleOrder, self).create(vals)

FasSaleOrder()
