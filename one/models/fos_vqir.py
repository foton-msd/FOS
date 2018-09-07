# -*- coding: utf-8 -*-
import psycopg2
import datetime
from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class FosVqir(models.Model):
  _name = 'fos.vqir'

  name = fields.Char(string="VQIR", required=True, default='Auto-generated', readonly=True, copy=False)
  vqir_date = fields.Date(string="Date", required=True)
  preapproved_date = fields.Date(string="Pre-Approved Date", readonly=True)
  preclaim_number = fields.Char(string="Pre-Claim Reference", copy=False)
  payment_receipt = fields.Char(string="PR Reference", copy=False)
  vqir_type = fields.Selection(string="Type", selection=[('warranty', 'Warranty'),('service','Service')], required=True)
  vqir_service_type = fields.Selection(string="Servive Type", selection=[('pmp','PMS'),('gj','General Job'),
    ('br','Body Repair')])
  vqir_state = fields.Selection(string="Status", copy=False, selection=[
      ('draft', 'Draft'),
      ('cancel', 'Cancelled'),
      ('submit', 'Submitted'),
      ('ack','Acknowledged'),
      ('approved','Approved'),
      ('disapproved','Disapproved'),
      ('declined','Declined'),
      ('preclaimed','Pre-claimed'),
      ('paid','Paid')
    ], default='draft', readonly=True)
  vqir_state_logs = fields.Text(string="Status Logs", readonly=True)

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
  pj_parts_total = fields.Float(string="Total", compute="_getPJPartsTotal", readonly=True)
  pj_job_total = fields.Float(string="Total", compute="_getPJJobTotal", readonly=True)
  # parts and jobs
  fos_vqir_parts_and_jobs_line = fields.One2many(string="Parts & Jobs", comodel_name="fos.vqir.parts.and.jobs", inverse_name="fos_vqir_id", ondelete="cascade")
  # images
  fos_vqir_images_line = fields.One2many(string="Images", comodel_name="fos.vqir.images", inverse_name="fos_vqir_id", ondelete="cascade")  
  company_id = fields.Many2one(string="Company", comodel_name="res.company", required=True, copy=True)

  @api.model
  def create(self, vals):
    vals['name'] = self.env['ir.sequence'].next_by_code('fos.vqir.seq')
    result = super(FosVqir, self).create(vals)
    return result
    
  @api.multi
  def action_cancel(self):
    self.write({'vqir_state': 'cancel'})
        
  @api.multi
  def _getPJTotal(self):
    for line in self.fos_vqir_parts_and_jobs_line:
      self.pj_total += line.parts_total + line.job_total
    return self.pj_total

  @api.multi
  def _getPJPartsTotal(self):
    for line in self.fos_vqir_parts_and_jobs_line:
      self.pj_parts_total += line.parts_total
    return self.pj_parts_total

  @api.multi
  def _getPJJobTotal(self):
    for line in self.fos_vqir_parts_and_jobs_line:
      self.pj_job_total += line.job_total
    return self.pj_job_total

  @api.multi
  def action_submit(self):
    vqir_state_logs = "Document:" + self.name + "\n" + \
      "Submitted by: " + self.env.user.name + "\n" + \
      "Submitted at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
      "--------------------------------------------------\n"
    self.write({'vqir_state': 'submit',
      'vqir_state_logs': vqir_state_logs + (self.vqir_state_logs or '')})  
    # set connection parameters to FMPI
    conn_string = "host='" + self.company_id.fmpi_host + \
      "' dbname='"+ self.company_id.fmpi_pgn + \
      "' user='"+ self.company_id.fmpi_pgu + \
      "' password='"+ self.company_id.fmpi_pgp + "'"
    logger.info("connecting to the database\n ->%s"%(conn_string))
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    # set upload string (SQL)
    cursor.execute("""INSERT INTO fmpi_vqir (name, vqir_date, preapproved_date, preclaim_number, 
      payment_receipt, vqir_type, vqir_service_type, vqir_state, date_occur, vqir_city, place_of_incident, 
      km_1st_trouble, run_km, part, person, others, trouble_explanation, trouble_cause_analysis, disposal_measures,
      proposal_for_improvement, driver_name, ss_name, ss_street1, ss_street2, ss_city, ss_phone, 
      ss_mobile, ss_fax, ss_email, users_name, users_street1, users_street2, users_city, users_phone, 
      users_mobile, users_fax, users_email, date_released, reps_name, reps_street1, reps_street2, 
      reps_city, reps_phone, reps_mobile, reps_fax, reps_email, fos_fu_id, dealer_id, dealer_vqir_id, 
      dealer_host, dealer_db, dealer_port, dealer_pgu, dealer_pgp, vqir_state_logs) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
      %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
      %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s);
      """,(self.name or None, 
      self.vqir_date or None, 
      self.preapproved_date or None, 
      self.preclaim_number or None, 
      self.payment_receipt or None, 
      self.vqir_type or None, 
      self.vqir_service_type or None, 
      'submit',             
      self.date_occur or None, 
      self.vqir_city or None, 
      self.place_of_incident or None, 
      self.km_1st_trouble or None, 
      self.run_km or None, 
      self.part or None, 
      self.person or None, 
      self.others or None, 
      self.trouble_explanation or None, 
      self.trouble_cause_analysis or None, 
      self.disposal_measures or None,
      self.proposal_for_improvement or None, 
      self.driver_name or None, 
      self.ss_name or None, 
      self.ss_street1 or None, 
      self.ss_street2 or None, 
      self.ss_city or None, 
      self.ss_phone or None, 
      self.ss_mobile or None, 
      self.ss_fax or None, 
      self.ss_email or None, 
      self.users_name or None, 
      self.users_street1 or None, 
      self.users_street2 or None, 
      self.users_city or None, 
      self.users_phone or None, 
      self.users_mobile or None, 
      self.users_fax or None, 
      self.users_email or None, 
      self.date_released or None, 
      self.reps_name or None, 
      self.reps_street1 or None, 
      self.reps_street2 or None, 
      self.reps_city or None, 
      self.reps_phone or None, 
      self.reps_mobile or None, 
      self.reps_fax or None, 
      self.reps_email or None, 
      self.fos_fu_id.id or None, 
      self.company_id.dealer_id.id, 
      self.id, 
      self.company_id.dealer_host, 
      self.company_id.dealer_pgn, 
      self.company_id.dealer_port, 
      self.company_id.dealer_pgu, 
      self.company_id.dealer_pgp, 
      self.vqir_state_logs))    
    # vqir jobs and parts
    for ji in self.fos_vqir_parts_and_jobs_line:
      cursor.execute("""INSERT INTO fmpi_vqir_parts_and_jobs (
        name, fmpi_vqir_id, si_number, si_date, parts_number, parts_desc, 
        parts_qty, parts_cost, parts_with_fee, parts_total, job_code, 
        job_code_desc, job_qty, job_cost, job_total, job_parts_total, 
        remarks) VALUES (%s,(SELECT id FROM fmpi_vqir ORDER BY id DESC LIMIT 1),
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""",
        (ji.name or None, 
        ji.si_number or None, 
        ji.si_date or None, 
        ji.parts_number or None, 
        ji.parts_desc or None, 
        ji.parts_qty or None, 
        ji.parts_cost or None, 
        ji.parts_with_fee or None, 
        ji.parts_total or None, 
        ji.job_code or None, 
        ji.job_code_desc or None, 
        ji.job_qty or None, 
        ji.job_cost or None, 
        ji.job_total or None, 
        ji.job_parts_total or None, 
        ji.remarks or None))
    for img in self.fos_vqir_images_line:
      cursor.execute("""
          INSERT INTO fmpi_vqir_images (
            name, fmpi_vqir_id, image_variant, image, image_medium, 
            image_small, remarks) VALUES (
              %s, (SELECT id FROM fmpi_vqir ORDER BY id DESC LIMIT 1),
              %s, %s, %s, %s, %s);
        """,(
          img.name or None, img.image_variant or None, 
          img.image or None, img.image_medium or None,
          img.image_small or None, img.remarks or None
        ))
    conn.commit()
    conn.close()
        

FosVqir()
