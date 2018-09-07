# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError
from odoo import models, fields, api, exceptions, _
import logging
logger = logging.getLogger(__name__)

class FasSaleOrder(models.Model):
  _inherit = 'sale.order'
  
  so_type = fields.Selection(string="Order Type", required=True, readonly=True, states={'draft': [('readonly', False)]},
    selection=[('units','Units'),('parts','Parts'),('service','Service'),('addoncost','Add-on Cost')])
  run_km = fields.Integer(string="Run KM")
  fas_area_id = fields.Many2one(string="Area", comodel_name="fas.area")
  job_type = fields.Selection(string="Job Type",
    selection=[('major_repair','Major Repair'),
      ('minor_repair','Minor Repair'),
      ('body_repair_insurance','Body Repair Insurance'),
      ('body_repair','Body Repair'),
      ('pms','PMS'),
      ('otc','OTC'),
      ('general_job','General Job'),
      ('warranty','Warranty')])
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
  
  @api.multi
  def print_fos_quotation(self):
    return self.env.ref('sale.action_report_saleorder').report_action(self)

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
    if self.so_type == 'service':
      validated = self.check_limit()
    elif self.so_type == 'parts':
      validated = self.check_limit()

    logger.info("Validation Result: " + str(validated))
 
    if validated:
      self.write({
          'sq_number': self.name,
          'name': self.env['ir.sequence'].next_by_code('fas.so.seq')})
      self._action_confirm()
      if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
        self.action_done()
      if self.so_type == 'units':        
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
  def action_cancel(self, a_value):
    if self.so_type == "units" and self.state == "sale":
      lines = self.order_line
      if lines:
        for line in lines:
          if line.fu_id.product_id.id == line.product_id.id:
            fu_obj = self.pool.get("fas.fu")
            if fu_obj:
              super(FasSaleOrder,self).action_cancel()
              fu_obj.write(line.fu_id, {'active': True, 'state': 'avail', 'so_line_id': None})
            else:
              super(FasSaleOrder,self).action_cancel()

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
FasSaleOrder()
