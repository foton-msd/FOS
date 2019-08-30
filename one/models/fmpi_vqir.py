# -*- coding: utf-8 -*-
import socket
import datetime
from odoo import models, fields, api
from xmlrpc import client as xmlrpclib
import logging
logger = logging.getLogger(__name__)

class FMPIVqir(models.Model):
  _name = 'fmpi.vqir'
  _description = 'FMPI VQIR'
  _sql_constraints = [
  ('vqir_record_unique', 'unique(name,dealer_id)','VQIR Number already exists!')]

  name = fields.Char(string="VQIR", readonly=True)
  vqir_date = fields.Datetime(string="Date", readonly=True)
  preapproved_date = fields.Date(string="Pre-Approved Date", readonly=True)
  preclaim_number = fields.Char(string="Pre-Claim Reference", readonly=True)
  payment_receipt = fields.Char(string="PR Reference", readonly=True)
  vqir_type = fields.Selection(string="Type", selection=[('warranty', 'Warranty'),('service','Service'),('tsb','TSB'),('first_pms','First PMS')], readonly=True)
  vqir_service_type = fields.Selection(string="Servive Type", selection=[('pmp','PMS'),('gj','General Job'),
    ('br','Body Repair')], readonly=True)
  vqir_state = fields.Selection(string="Status", selection=[
      ('draft', 'Draft'),
      ('cancel', 'Cancelled'),
      ('submit', 'Submitted'),
      ('ack','Acknowledged'),
      ('approved','Approved'),
      ('disapproved','Disapproved'),
      ('declined','Returned'),
      ('paid','Paid')
    ], default='draft', readonly=True)
  vqir_state_logs = fields.Text(string="Status Logs", readonly=True)
  date_occur = fields.Date(string="Date of occurence", readonly=True)
  vqir_city = fields.Char(string="City", readonly=True)
  place_of_incident = fields.Char(string="Place of incident", readonly=True)
  km_1st_trouble = fields.Integer(string="KM of first trouble happened", readonly=True)
  run_km = fields.Integer(string="Run KM", readonly=True)
  part = fields.Char(string="Part", readonly=True)
  person = fields.Char(string="Person", readonly=True)
  others = fields.Char(string="Other", readonly=True)
  trouble_explanation = fields.Text(string="Trouble Explanation", readonly=True)
  trouble_cause_analysis = fields.Text(string="Trouble Cause Analysis", readonly=True)
  disposal_measures = fields.Text(string="Disposal Measures", readonly=True)
  proposal_for_improvement = fields.Text(string="Proposal/Requirement for improvement", readonly=True)
  driver_name = fields.Char(string="Driver's  Name", readonly=True)
  # service station name fields
  ss_name = fields.Char(string="Service Station Name", readonly=True)
  ss_street1 = fields.Char(string="Address", readonly=True)
  ss_street2 = fields.Char(string=" ", readonly=True)
  ss_city = fields.Char(string="City", readonly=True)
  ss_phone = fields.Char(string="Phone", readonly=True)
  ss_mobile = fields.Char(string="Mobile", readonly=True)
  ss_fax = fields.Char(string="Fax", readonly=True)
  ss_email = fields.Char(string="Email", readonly=True)
  # user's info fields
  users_name = fields.Char(string="User's Name", readonly=True)
  users_street1 = fields.Char(string="Street 1", readonly=True)
  users_street2 = fields.Char(string="Street 2", readonly=True)
  users_city = fields.Char(string="City", readonly=True)
  users_phone = fields.Char(string="Phone", readonly=True)
  users_mobile = fields.Char(string="Mobile", readonly=True)
  users_fax = fields.Char(string="Fax", readonly=True)
  users_email = fields.Char(string="Email", readonly=True)
  date_released = fields.Date(string="Date Released", readonly=True)
  # reporters info fields
  reps_name = fields.Char(string="Reporter's Name", readonly=True)
  reps_street1 = fields.Char(string="Address", readonly=True)
  reps_street2 = fields.Char(string=" ", readonly=True)
  reps_city = fields.Char(string="City", readonly=True)
  reps_phone = fields.Char(string="Phone", readonly=True)
  reps_mobile = fields.Char(string="Mobile", readonly=True)
  reps_fax = fields.Char(string="Fax", readonly=True)
  reps_email = fields.Char(string="Email", readonly=True)
  # unit info fields
  fos_fu_id = fields.Many2one(string="FOTON Number", comodel_name="one.fu", readonly=True)
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
  remarks = fields.Text(string="Remarks", readonly=True)
  
  # parts and jobs
  fmpi_vqir_parts_and_jobs_line = fields.One2many(string="Parts & Jobs", comodel_name="fmpi.vqir.parts.and.jobs", inverse_name="fmpi_vqir_id", ondelete="cascade")
  # images
  fmpi_vqir_images_line = fields.One2many(string="Images", comodel_name="fmpi.vqir.images", inverse_name="fmpi_vqir_id", readonly=True, ondelete="cascade")
  # dealer info
  company_id = fields.Many2one(string="Company", comodel_name="res.company", required=False)
  dealer_id = fields.Many2one(string="Dealer Name", comodel_name="one.dealers", required=True)
  dealer_vqir_id = fields.Integer(string="VQIR ID", required=True)
  dealer_host = fields.Char(string="Host Name", required=True)
  dealer_db = fields.Char(string="Database Name", required=True)
  dealer_port = fields.Char(string="Port", required=True)
  dealer_pgu = fields.Char(string="PGU", required=True)
  dealer_pgp = fields.Char(string="PGP", required=True)
  # date
  approved_date = fields.Datetime(string="Approved Date")
  submitted_date = fields.Datetime(string="Submitted Date")
  declined_date = fields.Datetime(string="Returned Date")
  disapproved_date = fields.Datetime(string="Disapproved Date")
  ack_date = fields.Datetime(string="Acknowledge Date")
  paid_date = fields.Datetime(string="Paid Date")
  url = fields.Char(string="URL", readonly=True, required=True)
  db = fields.Char(string="Database", readonly=True, required=True)
  username = fields.Char(string="User Name", readonly=True, required=True)
  password = fields.Char(string="Password", readonly=True, required=True)  
  company_id = fields.Many2one(string="Company", comodel_name="res.company", required=False)


  @api.multi
  def action_ack_api(self):
   # 1. make connection to Dealer
    dealer_vqir_id = self.dealer_vqir_id
    db = self.db
    url = self.url
    username = self.username
    password = self.password
   # attempt to connect
    logger.info("URL: " + url)
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if not uid:
      raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
      return 
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    vqir_state_logs = "Document:" + self.name + "\n" + \
      "Acknowledged by: " + self.env.user.name + "\n" + \
      "Acknowledged at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
      "Acknowledgement notes: " + (self.name or '') + "\n" + \
      "--------------------------------------------------\n"
    self.write({'vqir_state': 'ack',
      'vqir_state_logs': str(self.vqir_state_logs or '')}) 
    cur_stamp = fields.datetime.now()
    if models:
      logger.info("Models: " + str(models))
      mod_out = models.execute_kw(db, uid, password, 'fos.vqir', 'write', 
        [[self.dealer_vqir_id,], {'vqir_state': 'ack','vqir_state_logs': str(self.vqir_state_logs or ''),
        "ack_date":cur_stamp}])
      for line in self.fmpi_vqir_parts_and_jobs_line:
        pj_approved_amount = models.execute_kw(db, uid, password, 'fos.vqir.parts.and.jobs', 'write', 
        [[line.dealer_pj_id,], {'approved_amount': line.approved_amount,
        'job_approved_amount': line.job_approved_amount}])
    self.write({'vqir_state': 'ack', "ack_date":cur_stamp})

  @api.multi
  def action_app_api(self):
   # 1. make connection to Dealer
    dealer_vqir_id = self.dealer_vqir_id
    db = self.db
    url = self.url
    username = self.username
    password = self.password
   # attempt to connect
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if not uid:
      raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
      return 
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    vqir_state_logs = "Document:" + self.name + "\n" + \
      "Approved by: " + self.env.user.name + "\n" + \
      "Approved at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
      "Approved notes: " + (self.name or '') + "\n" + \
      "--------------------------------------------------\n"
    self.write({'vqir_state': 'approved',
      'vqir_state_logs': str(self.vqir_state_logs or '')}) 
    cur_stamp = fields.datetime.now()
    if models:
      logger.info("Models: " + str(models))
      mod_out = models.execute_kw(db, uid, password, 'fos.vqir', 'write', 
        [[self.dealer_vqir_id,], {'vqir_state': 'approved','vqir_state_logs': str(self.vqir_state_logs or ''),
        "approved_date":cur_stamp}])
      for line in self.fmpi_vqir_parts_and_jobs_line:
            pj_approved_amount = models.execute_kw(db, uid, password, 'fos.vqir.parts.and.jobs', 'write', 
        [[line.dealer_pj_id,], {'approved_amount': line.approved_amount,
        'job_approved_amount': line.job_approved_amount}])
    self.write({'vqir_state': 'approved', "approved_date":cur_stamp})

  @api.multi
  def action_dis_api(self):
   # 1. make connection to Dealer
    dealer_vqir_id = self.dealer_vqir_id
    db = self.db
    url = self.url
    username = self.username
    password = self.password
   # attempt to connect
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if not uid:
      raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
      return 
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    vqir_state_logs = "Document:" + self.name + "\n" + \
      "Disapproved by: " + self.env.user.name + "\n" + \
      "Disapproved at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
      "Disapproved notes: " + (self.name or '') + "\n" + \
      "--------------------------------------------------\n"
    self.write({'vqir_state': 'disapproved',
      'vqir_state_logs': str(self.vqir_state_logs or '')}) 
    cur_stamp = fields.datetime.now()
    if models:
      logger.info("Models: " + str(models))
      mod_out = models.execute_kw(db, uid, password, 'fos.vqir', 'write', 
        [[self.dealer_vqir_id,], {'vqir_state': 'disapproved','vqir_state_logs': str(self.vqir_state_logs or ''),
        "disapproved_date":cur_stamp}])
    self.write({'vqir_state': 'disapproved', "disapproved_date":cur_stamp})

  @api.multi
  def action_dec_api(self):
   # 1. make connection to Dealer
    dealer_vqir_id = self.dealer_vqir_id
    db = self.db
    url = self.url
    username = self.username
    password = self.password
   # attempt to connect
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if not uid:
      raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
      return 
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    vqir_state_logs = "Document:" + self.name + "\n" + \
      "Returned by: " + self.env.user.name + "\n" + \
      "Returned at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
      "Returned notes: " + (self.name or '') + "\n" + \
      "--------------------------------------------------\n"
    self.write({'vqir_state': 'declined',
      'vqir_state_logs': str(self.vqir_state_logs or '')}) 
    cur_stamp = fields.datetime.now()
    if models:
      logger.info("Models: " + str(models))
      mod_out = models.execute_kw(db, uid, password, 'fos.vqir', 'write', 
        [[self.dealer_vqir_id,], {'vqir_state': 'declined','vqir_state_logs': str(self.vqir_state_logs or ''),
        "declined_date":cur_stamp}])
    self.write({'vqir_state': 'declined', "declined_date":cur_stamp})

  @api.multi
  def action_pd_api(self):
   # 1. make connection to Dealer
    dealer_vqir_id = self.dealer_vqir_id
    db = self.db
    url = self.url
    username = self.username
    password = self.password
   # attempt to connect
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if not uid:
      raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
      return 
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    vqir_state_logs = "Document:" + self.name + "\n" + \
      "Paid by: " + self.env.user.name + "\n" + \
      "Paid at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
      "Paid notes: " + (self.name or '') + "\n" + \
      "--------------------------------------------------\n"
    self.write({'vqir_state': 'paid',
      'vqir_state_logs': str(self.vqir_state_logs or '')}) 
    cur_stamp = fields.datetime.now()
    if models:
      logger.info("Models: " + str(models))
      mod_out = models.execute_kw(db, uid, password, 'fos.vqir', 'write', 
        [[self.dealer_vqir_id,], {'vqir_state': 'paid','vqir_state_logs': str(self.vqir_state_logs or ''),
        "paid_date":cur_stamp}])
    self.write({'vqir_state': 'paid', "paid_date":cur_stamp})


  @api.one
  def _getPJTotal(self):
    pj_total = 0
    for line in self.fmpi_vqir_parts_and_jobs_line:
      pj_total += line.parts_total + line.job_total
    self.pj_total = pj_total

  @api.one
  def _getPJPartsTotal(self):
    pj_parts_total = 0
    for line in self.fmpi_vqir_parts_and_jobs_line:
      pj_parts_total += line.parts_total
    self.pj_parts_total = pj_parts_total

  @api.one
  def _getPJJobTotal(self):
    pj_job_total = 0
    for line in self.fmpi_vqir_parts_and_jobs_line:
      pj_job_total += line.job_total
    self.pj_job_total = pj_job_total

  @api.one
  def _getApprovedTotal(self):
    pj_approved_total = 0
    for line in self.fmpi_vqir_parts_and_jobs_line:
      pj_approved_total += line.job_parts_approved_total
    self.pj_approved_total = pj_approved_total

FMPIVqir()
