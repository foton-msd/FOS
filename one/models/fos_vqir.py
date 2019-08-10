# -*- coding: utf-8 -*-
import datetime
import socket
from odoo import models, fields, api
from xmlrpc import client as xmlrpclib
import logging
logger = logging.getLogger(__name__)

class FosVqir(models.Model):
  _name = 'fos.vqir'

  name = fields.Char(string="VQIR", required=True, default='Auto-generated', readonly=True, copy=False)
  vqir_date = fields.Datetime(string="Date", required=True)
  preapproved_date = fields.Date(string="Pre-Approved Date", readonly=True)
  preclaim_number = fields.Char(string="Pre-Claim Reference", copy=False)
  payment_receipt = fields.Char(string="PR Reference", copy=False)
  vqir_type = fields.Selection(string="Type", selection=[('warranty', 'Warranty'),('service','Service'),('tsb','TSB'),('first_pms','First PMS')], required=True)
  vqir_service_type = fields.Selection(string="Servive Type", selection=[('pmp','PMS'),('gj','General Job'),
    ('br','Body Repair')])
  vqir_state = fields.Selection(string="Status", copy=False, selection=[
      ('draft', 'Draft'),
      ('cancel', 'Cancelled'),
      ('submit', 'Submitted'),
      ('ack','Acknowledged'),
      ('approved','Approved'),
      ('disapproved','Disapproved'),
      ('declined','Returned'),
      ('paid','Paid')
    ], default='draft', readonly=True)
  vqir_state_logs = fields.Text(string="Status Logs", readonly=True, copy=False)

  date_occur = fields.Date(string="Date of occurence", required=True)
  #one_vqir_city_id = fields.Many2one(string="City", comodel_name="one.vqir.cities", required=True)
  vqir_city = fields.Char(string="City")
  place_of_incident = fields.Char(string="Place of incident")
  km_1st_trouble = fields.Integer(string="KM of first trouble happened")
  run_km = fields.Integer(string="Run KM")
  part = fields.Char(string="Part")
  person = fields.Char(string="Person")
  others = fields.Char(string="Other")
  trouble_explanation = fields.Text(string="Trouble Explanation")
  trouble_cause_analysis = fields.Text(string="Trouble Cause Analysis")
  disposal_measures = fields.Text(string="Disposal Measures")
  proposal_for_improvement = fields.Text(string="Proposal/Requirement for improvement")
  driver_name = fields.Char(string="Driver's  Name")
  # service station name fields
  ss_name = fields.Char(string="Service Station Name")
  ss_street1 = fields.Char(string="Address")
  ss_street2 = fields.Char(string=" ")
  ss_city = fields.Char(string="City")
  ss_phone = fields.Char(string="Phone")
  ss_mobile = fields.Char(string="Mobile")
  ss_fax = fields.Char(string="Fax")
  ss_email = fields.Char(string="Email")
  # user's info fields
  users_name = fields.Char(string="User's Name")
  users_street1 = fields.Char(string="Street 1")
  users_street2 = fields.Char(string="Street 2")
  users_city = fields.Char(string="City")
  users_phone = fields.Char(string="Phone")
  users_mobile = fields.Char(string="Mobile")
  users_fax = fields.Char(string="Fax")
  users_email = fields.Char(string="Email")
  date_released = fields.Date(string="Date Released")
  # reporters info fields
  reps_name = fields.Char(string="Reporter's Name")
  reps_street1 = fields.Char(string="Address")
  reps_street2 = fields.Char(string=" ")
  reps_city = fields.Char(string="City")
  reps_phone = fields.Char(string="Phone")
  reps_mobile = fields.Char(string="Mobile")
  reps_fax = fields.Char(string="Fax")
  reps_email = fields.Char(string="Email")
  # unit info fields
  fos_fu_id = fields.Many2one(string="FOTON Number", comodel_name="one.fu", required=True)
  fu_local_name = fields.Char(string="Local Name", related="fos_fu_id.fmpi_fu_local_name_id.name", readonly=True)
  fu_description = fields.Char(string="Description", related="fos_fu_id.description", readonly=True)
  fu_body_type = fields.Char(string="Body Type", related="fos_fu_id.body_type", readonly=True)
  fu_chassis_number = fields.Char(string="Chassis Number", related="fos_fu_id.chassis_number", readonly=True)
  fu_engine_number = fields.Char(string="Engine Number", related="fos_fu_id.engine_number", readonly=True)
  fu_conduction_sticker = fields.Char(string="Conduction Sticker", related="fos_fu_id.conduction_sticker", readonly=True)
  fu_plate_number = fields.Char(string="Plate Number", related="fos_fu_id.plate_number", readonly=True)
  fu_owner_name = fields.Char(string="Owner Name", related="fos_fu_id.owner_name", readonly=True)
  fu_owner_address = fields.Char(string="Address", related="fos_fu_id.owner_address", readonly=True)
  fu_color = fields.Char(string="Color", related="fos_fu_id.color", readonly=True)
  pj_total = fields.Float(string="Total", compute="_getPJTotal", readonly=True)
  pj_parts_total = fields.Float(string="Parts Total", compute="_getPJPartsTotal", readonly=True)
  pj_job_total = fields.Float(string="Job Total", compute="_getPJJobTotal", readonly=True)
  pj_approved_total = fields.Float(string="Approved Total", compute="_getApprovedTotal", readonly=True)
  remarks = fields.Text(string="Remarks")
  # parts and jobs
  fos_vqir_parts_and_jobs_line = fields.One2many(string="Parts & Jobs", comodel_name="fos.vqir.parts.and.jobs", inverse_name="fos_vqir_id", ondelete="cascade")
  # images
  fos_vqir_images_line = fields.One2many(string="Images", comodel_name="fos.vqir.images", inverse_name="fos_vqir_id", ondelete="cascade")
  company_id = fields.Many2one(string="Company", comodel_name="res.company", required=False)
  # date
  approved_date = fields.Datetime(string="Approved Date")
  submitted_date = fields.Datetime(string="Submitted Date")
  declined_date = fields.Datetime(string="Returned Date")
  disapproved_date = fields.Datetime(string="Disapproved Date")
  ack_date = fields.Datetime(string="Acknowledge Date")
  paid_date = fields.Datetime(string="Paid Date")

  @api.model
  def create(self, vals):
    vals['company_id'] = self.env.user.company_id.id
    vals['name'] = self.env['ir.sequence'].next_by_code('fos.vqir.seq')
    result = super(FosVqir, self).create(vals)
    return result

  @api.multi
  def action_cancel(self):
    self.write({'vqir_state': 'cancel'})

  @api.one
  def _getPJTotal(self):
    pj_total = 0
    for line in self.fos_vqir_parts_and_jobs_line:
      pj_total += line.parts_total + line.job_total
    self.pj_total = pj_total

  @api.one
  def _getPJPartsTotal(self):
    pj_parts_total = 0
    for line in self.fos_vqir_parts_and_jobs_line:
      pj_parts_total += line.parts_total
    self.pj_parts_total = pj_parts_total

  @api.one
  def _getPJJobTotal(self):
    pj_job_total = 0
    for line in self.fos_vqir_parts_and_jobs_line:
      pj_job_total += line.job_total
    self.pj_job_total = pj_job_total

  @api.one
  def _getApprovedTotal(self):
    pj_approved_total = 0
    for line in self.fos_vqir_parts_and_jobs_line:
      pj_approved_total += line.job_parts_approved_total
    self.pj_approved_total = pj_approved_total

  @api.multi
  def action_submit_api(self):
    # 1. make connection to FMPI
    dealer_id = self.company_id.dealer_id.id

    # FMPI's API Connection Parameters
    url = self.company_id.fmpi_host.strip()
    db = self.company_id.fmpi_pgn
    username = self.company_id.fmpi_pgu
    password = self.company_id.fmpi_pgp
    vqir_number = self.name

    # connect to FMPI
    logger.info("Connecting to " + url)
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if not uid:
      raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
      return
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    cur_stamp = fields.datetime.now()

    # Query existence of dealer's VQIR from FMPI Database
    fmpi_existing_vqir = models.execute_kw(db, uid, password,
        'fmpi.vqir', 'search',
        [[['name', '=', vqir_number], ['dealer_id', '=', dealer_id], ['vqir_date', '=', self.vqir_date]]])
    if fmpi_existing_vqir:
      vqir_state_logs = "Document:" + (self.name or 'Empty Document') + "\n" + \
        "Re-submitted by: " + (self.env.user.name or 'No User Name specified') + "\n" + \
        "Re-submitted at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
        "--------------------------------------------------\n"
      self.write({'vqir_state': 'submit',
        'vqir_state_logs': vqir_state_logs + str(self.vqir_state_logs or ''),
        "submitted_date":cur_stamp})

      for existingID in fmpi_existing_vqir:
        fmpi_vqir_id = models.execute_kw(db, uid, password, 'fmpi.vqir', 'write', [[existingID], {
          'vqir_state': 'submit',
          'date_occur': self.date_occur,
          'vqir_city': self.vqir_city,
          'place_of_incident': self.place_of_incident,
          'km_1st_trouble': self.km_1st_trouble,
          'run_km': self.run_km,
          'person': self.person,
          'others': self.others,
          'trouble_explanation': self.trouble_explanation,
          'trouble_cause_analysis': self.trouble_cause_analysis,
          'disposal_measures': self.disposal_measures,
          'proposal_for_improvement': self.proposal_for_improvement,
          'driver_name': self.driver_name,
          'ss_name': self.ss_name,
          'ss_street1': self.ss_street1,
          'ss_street2': self.ss_street2,
          'ss_city': self.ss_city,
          'ss_phone': self.ss_phone,
          'ss_mobile': self.ss_mobile,
          'ss_fax': self.ss_fax,
          'ss_email': self.ss_email,
          'users_name': self.users_name,
          'users_street1': self.users_street1,
          'users_street2': self.users_street2,
          'users_city': self.users_city,
          'users_phone': self.users_phone,
          'users_mobile': self.users_mobile,
          'users_fax': self.users_fax,
          'users_email': self.users_email,
          'reps_name': self.reps_name,
          'reps_street1': self.reps_street1,
          'reps_street2': self.reps_street2,
          'reps_city': self.reps_city,
          'reps_phone': self.reps_phone,
          'reps_mobile': self.reps_mobile,
          'reps_fax': self.reps_fax,
          'reps_email': self.reps_email,
          'remarks': self.remarks,
          'fos_fu_id': self.fos_fu_id.id,
          'vqir_state_logs': self.vqir_state_logs,
          'submitted_date': fields.datetime.now(),
          'declined_date': self.declined_date,
          'disapproved_date': self.disapproved_date,
          'ack_date': self.ack_date,
          'paid_date': self.paid_date,
          'url': self.company_id.dealer_host.strip(),
          'db' : self.company_id.dealer_pgn,
          'username' : self.company_id.dealer_pgu,
          'password' : self.company_id.dealer_pgp}])
        # query IDs of parts and jobs from FMPI Database
        fmpi_existing_vqir_pj_ids = models.execute_kw(db, uid, password,
          'fmpi.vqir.parts.and.jobs', 'search', 
            [[['fmpi_vqir_id', '=', existingID]]])
        # delete parts and jobs from FMPI Database
        models.execute_kw(db, uid, password, 'fmpi.vqir.parts.and.jobs', 'unlink', [fmpi_existing_vqir_pj_ids])
        # re-create parts and jobs record based on Dealer's Database
        for ji in self.fos_vqir_parts_and_jobs_line:
          models.execute_kw(db, uid, password, 'fmpi.vqir.parts.and.jobs', 'create', [{
            'name': ji.name,
            'fmpi_vqir_id': existingID,
            'si_number':ji.si_number,
            'si_date':ji.si_date,
            'parts_number': ji.part_id.name,
            'parts_desc': ji.parts_desc,
            'parts_qty': ji.parts_qty,
            'parts_cost': ji.parts_cost,
            'parts_with_fee': ji.parts_with_fee,
            'parts_total': ji.parts_total,
            'job_code': ji.job_code,
            'job_code_desc': ji.job_code_desc,
            'job_qty': ji.job_qty,
            'job_cost': ji.job_cost,
            'dealer_pj_id': ji.id }])
        # query IDs of VQIR Images from FMPI Database
        fmpi_existing_vqir_images_ids = models.execute_kw(db, uid, password,
          'fmpi.vqir.images', 'search', 
            [[['fmpi_vqir_id', '=', existingID]]])
        # delete VQIR Images from FMPI Database
        models.execute_kw(db, uid, password, 'fmpi.vqir.images', 'unlink', [fmpi_existing_vqir_images_ids])
        # re-create VQIR Images record based on Dealer's Database
        for img in self.fos_vqir_images_line:
          models.execute_kw(db, uid, password, 'fmpi.vqir.images', 'create', [{
            'name': img.name,
            'fmpi_vqir_id': existingID,
            'image': img.image,
            'image_medium': img.image_medium,
            'image_small': img.image_small,
            'image_remarks': img.image_remarks,
            }])
    else:
      # 2. call fmpi.vqir model
      vqir_state_logs = "Document:" + (self.name or 'Empty Document') + "\n" + \
        "Submitted by: " + (self.env.user.name or 'No User Name specified') + "\n" + \
        "Submitted at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
        "--------------------------------------------------\n"
      self.write({'vqir_state': 'submit',
        'vqir_state_logs': vqir_state_logs + str(self.vqir_state_logs or ''),
        "submitted_date":cur_stamp})
      fmpi_vqir_id = models.execute_kw(db, uid, password, 'fmpi.vqir', 'create', [{
        'dealer_id': self.company_id.dealer_id.id,
        'name': self.name,
        'vqir_date':self.vqir_date,
        'preapproved_date': self.preapproved_date,
        'payment_receipt': self.payment_receipt,
        'vqir_type': self.vqir_type,
        'vqir_service_type': self.vqir_service_type,
        'vqir_state': 'submit',
        'date_occur': self.date_occur,
        'vqir_city': self.vqir_city,
        'place_of_incident': self.place_of_incident,
        'km_1st_trouble': self.km_1st_trouble,
        'run_km': self.run_km,
        'part': self.part,
        'person': self.person,
        'others': self.others,
        'trouble_explanation': self.trouble_explanation,
        'trouble_cause_analysis': self.trouble_cause_analysis,
        'disposal_measures': self.disposal_measures,
        'proposal_for_improvement': self.proposal_for_improvement,
        'driver_name': self.driver_name,
        'ss_name': self.ss_name,
        'ss_street1': self.ss_street1,
        'ss_street2': self.ss_street2,
        'ss_city': self.ss_city,
        'ss_phone': self.ss_phone,
        'ss_mobile': self.ss_mobile,
        'ss_fax': self.ss_fax,
        'ss_email': self.ss_email,
        'users_name': self.users_name,
        'users_street1': self.users_street1,
        'users_street2': self.users_street2,
        'users_city': self.users_city,
        'users_phone': self.users_phone,
        'users_mobile': self.users_mobile,
        'users_fax': self.users_fax,
        'users_email': self.users_email,
        'date_released': self.date_released,
        'reps_name': self.reps_name,
        'reps_street1': self.reps_street1,
        'reps_street2': self.reps_street2,
        'reps_city': self.reps_city,
        'reps_phone': self.reps_phone,
        'reps_mobile': self.reps_mobile,
        'reps_fax': self.reps_fax,
        'reps_email': self.reps_email,
        'remarks': self.remarks,
        'fos_fu_id': self.fos_fu_id.id,
        'dealer_id': dealer_id,
        'dealer_vqir_id': self.id,
        'dealer_host': self.company_id.dealer_host,
        'dealer_db': self.company_id.dealer_pgn,
        'dealer_port': self.company_id.dealer_port,
        'dealer_pgu': self.company_id.dealer_pgu,
        'dealer_pgp': self.company_id.dealer_pgp,
        'vqir_state_logs': self.vqir_state_logs,
        'approved_date': self.approved_date,
        'submitted_date': fields.datetime.now(),
        'declined_date': self.declined_date,
        'disapproved_date': self.disapproved_date,
        'ack_date': self.ack_date,
        'paid_date': self.paid_date,
        'url': self.company_id.dealer_host.strip(),
        'db' : self.company_id.dealer_pgn,
        'username' : self.company_id.dealer_pgu,
        'password' : self.company_id.dealer_pgp
          }])

      if fmpi_vqir_id:
        logger.info("VQIR ID " + str(fmpi_vqir_id))
        # vqir jobs and parts
        for ji in self.fos_vqir_parts_and_jobs_line:
          fmpi_vqir_parts_and_jobs_id = models.execute_kw(db, uid, password, 'fmpi.vqir.parts.and.jobs', 'create', [{
            'name': ji.name,
            'fmpi_vqir_id': fmpi_vqir_id,
            'si_number':ji.si_number,
            'si_date':ji.si_date,
            'parts_number': ji.part_id.name,
            'parts_desc': ji.parts_desc,
            'parts_qty': ji.parts_qty,
            'parts_cost': ji.parts_cost,
            'parts_with_fee': ji.parts_with_fee,
            'parts_total': ji.parts_total,
            'job_code': ji.job_code,
            'job_code_desc': ji.job_code_desc,
            'job_qty': ji.job_qty,
            'job_cost': ji.job_cost,
            'approved_amount': ji.approved_amount,
            'dealer_pj_id': ji.id }])

        # vqir images
        for img in self.fos_vqir_images_line:
          fmpi_vqir_images_id = models.execute_kw(db, uid, password, 'fmpi.vqir.images', 'create', [{
            'name': img.name,
            'fmpi_vqir_id': fmpi_vqir_id,
            'image': img.image,
            'image_medium': img.image_medium,
            'image_small': img.image_small,
            'image_remarks': img.image_remarks,
            }])


FosVqir()
