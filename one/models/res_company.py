from odoo import models, fields, api
from xmlrpc import client as xmlrpclib
import psycopg2
from odoo.exceptions import UserError
import logging
logger = logging.getLogger(__name__)

class FasResCompany(models.Model):
  _inherit = 'res.company'
  dealer_id = fields.Many2one(string="Dealer ID", comodel_name="one.dealers")
  is_fmpi = fields.Boolean(string="Is FMPI?")
  fmpi_host = fields.Char(string="FMPI Host")
  fmpi_port = fields.Char(string="FMPI Port")
  fmpi_pgu = fields.Char(string="FMPI PG User Name")
  fmpi_pgp = fields.Char(string="FMPI PG Password")
  fmpi_pgn = fields.Char(string="FMPI PG DB")
  dealer_host = fields.Char(string="Dealer Host")
  dealer_port = fields.Char(string="Dealer Port")
  dealer_pgu = fields.Char(string="Dealer PG User Name")
  dealer_pgp = fields.Char(string="Dealer PG Password")
  dealer_pgn = fields.Char(string="Dealer PG DB")
  ams_host = fields.Char(string="AMS Host")
  ams_port = fields.Char(string="AMS Port")
  ams_pgu = fields.Char(string="AMS PG User Name")
  ams_pgp = fields.Char(string="AMS PG Password")
  ams_pgn = fields.Char(string="AMS PG DB")
  api_host = fields.Char(string="API Host")
  api_user = fields.Char(string="API User Name")
  api_pass = fields.Char(string="API Password")
  inet_url = fields.Char(string="I-Net Host")
  inet_user = fields.Char(string="I-Net User Name")
  inet_pass = fields.Char(string="I-Net Password")
  parts_categ_id = fields.Many2one(string="Parts Category", comodel_name="product.category")
  service_categ_id = fields.Many2one(string="Service Category", comodel_name="product.category")
  warranty_categ_id = fields.Many2one(string="Warranty Category", comodel_name="product.category")

  @api.multi
  def action_sync_local_names(self):
    # set connection parameters to AMS
    conn_string = "host='" + self.ams_host + \
      "' dbname='"+ self.ams_pgn + \
      "' user='"+ self.ams_pgu + \
      "' password='"+ self.ams_pgp + "'"
    logger.info("connecting to the database\n ->%s"%(conn_string))
    conn = psycopg2.connect(conn_string)
    if conn:
      cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
      logger.info("Local Names: Executing Query to AMS....")
      cursor.execute("SELECT * FROM fu_local_names ORDER BY id;")
      result_set = cursor.fetchall()
      if(result_set):
        ln_obj = self.env['one.local.names']
        r = 0
        for res in result_set:
          r+=1
          logger.info("Checking existence of Local Names: (" + str(res['id']) + ") "+ (res['local_name'] or ''))
          ln = ln_obj.search([('id','=',res['id'])])
          if not ln:
            logger.info("Local Name: (" + str(res['id']) + ") "+ (res['local_name'] or '') + " does not exists!...creating new dealer")
            self.env.cr.execute("""
              INSERT INTO one_local_names (id, name, classification, fmpi_fu_local_name_stamp)
              VALUES (%s,%s,%s,%s);
              """,(res['id'], res['local_name'], res['classification'], res['modified']))
          elif res['modified'] != ln.fmpi_fu_local_name_stamp:
            logger.info("Local Name: (" + str(res['id']) + ") "+ (res['local_name'] or '') + " is changed. Updating...")
            d_obj.write({
              'name': res['local_name'],
              'classification': res['classification'],
              'fmpi_fu_local_name_stamp': res['modified']
            })
          else:
            logger.info("Local Names: Nothing changed...skipping")
    conn.close()

  @api.multi
  def action_sync_dealers(self):
    # set connection parameters to AMS
    conn_string = "host='" + self.ams_host + \
      "' dbname='"+ self.ams_pgn + \
      "' user='"+ self.ams_pgu + \
      "' password='"+ self.ams_pgp + "'"
    logger.info("connecting to the database\n ->%s"%(conn_string))
    conn = psycopg2.connect(conn_string)
    if conn:
      cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
      logger.info("Dealers: Executing Query to AMS....")
      cursor.execute("""
        select id, dealer_code, dealer_name, address1, address2, city, zip, 
        telephone1, telephone2, fax, email, modified, region, 
        type, is_service from (select d.*, case when pg.group_name ilike 'dealer%' 
        then 'Dealer' else 'Non-Dealer' end::text as type from dealers d 
        left join dealer_groups dg on dg.dealer_id = d.id
        left join partner_groups pg on dg.partner_group_id = pg.id
        group by d.id, pg.group_name) as g
        group by id, dealer_code, dealer_name, 
        address1, address2, city, zip, telephone1, telephone2,
        fax, email, modified, region, type, is_service;
      """)
      result_set = cursor.fetchall()
      if(result_set):
        d_obj = self.env['one.dealers']
        r = 0
        for res in result_set:
          r+=1
          logger.info("Checking existence of Dealer: (" + str(r) + ") "+ (res['dealer_name'] or ''))
          d = d_obj.search([('id','=',res['id'])])
          if not d:
            logger.info("Dealer: (" + str(r) + ") "+ (res['dealer_name'] or '') + " does not exists!...creating new dealer")
            self.env.cr.execute("""
              INSERT INTO one_dealers (id, code, name, street1, street2, city, province, 
                zip, region, phone, fax, mobile, email, type, is_servicing, fmpi_dealer_stamp) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
              """,(res['id'], res['dealer_code'], res['dealer_name'], res['address1'], 
              res['address2'],res['city'],res['region'],res['zip'],res['region'],
              res['telephone1'],res['fax'],res['telephone2'],res['email'],res['type'],
              res['is_service'],res['modified']))
          elif res['modified'] != d.fmpi_dealer_stamp:
            logger.info("Dealer: (" + str(r) + ") "+ (res['dealer_name'] or '') + " is changed. Updating...")
            d_obj.write({
              'code': res['dealer_code'],
              'name': res['dealer_name'],
              'street1': res['address1'],
              'street2': res['address2'],
              'city': res['city'],
              'province': res['region'],
              'zip': res['zip'],
              'region': res['region'],
              'phone': res['telephone1'],
              'fax': res['fax'],
              'mobile': res['telephone2'],
              'email': res['email'],
              'type': res['type'],
              'is_servicing': res['is_service'],
              'fmpi_dealer_stamp': res['modified']
            })
          else:
            logger.info("Dealer: Nothing changed...skipping")

  @api.multi
  def action_sync_parts(self):
    # set connection parameters to FMPI
    conn_string = "host='" + self.fmpi_host + \
      "' dbname='"+ self.fmpi_pgn + \
      "' user='"+ self.fmpi_pgu + \
      "' password='"+ self.fmpi_pgp + "'"
    logger.info("connecting to the database\n ->%s"%(conn_string))
    conn = psycopg2.connect(conn_string)
    if conn:
      cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
      # set upload string (SQL)
      logger.info("Executing FMPI Query....")
      cursor.execute("""SELECT * FROM product_template     
        WHERE sub_type = 'parts';""")
      result_set = cursor.fetchall()
      if(result_set):
        pt_obj = self.env['product.template']
        r = 0
        for res in result_set:
          r+=1
          logger.info("Checking existence of Part Number: (" + str(r) + ") "+ (res['name'] or ''))
          ptr = pt_obj.search([('name','=',res['name'])])
          if not ptr:
            logger.info("Part Number: (" + str(r) + ") "+ (res['name'] or '') + " does not exists!...creating new product_template")
            ptr.create({
              'name': res['name'],
              'description': res['description'],
              'description_sale': res['description_sale'],
              'description_purchase': res['description_purchase'],
              'description_picking': res['description_picking'],
              'description_pickingin': res['description_pickingin'],
              'description_pickingout': res['description_pickingout'],
              'type': res['type'],
              'sale_ok': res['sale_ok'],
              'purchase_ok': res['purchase_ok'],
              'sub_type': res['sub_type'],
              'categ_id': self.parts_categ_id.id,
              'list_price': res['list_price'],
              'model': res['model'],
              'model_code': res['model_code'],
              'invoice_policy': res['invoice_policy'],
              'purchase_method': res['purchase_method'],
              'inner_code': res['inner_code'],
              'segment': res['segment'] ,
              'fmpi_product': True,
              'fmpi_product_id': res['id'],
              'write_date': res['fmpi_product_write_date']
            })
          elif res['fmpi_product_write_date'] != ptr.write_date:
              logger.info("Part Number: (" + str(r) + ") "+ (res['name'] or '') + " has changes. Updating...")
              ptr.write({
                'name': res['name'],
                'description': res['description'],
                'description_sale': res['description_sale'],
                'description_purchase': res['description_purchase'],
                'description_picking': res['description_picking'],
                'description_pickingin': res['description_pickingin'],
                'description_pickingout': res['description_pickingout'],
                'list_price': res['list_price'],
                'model': res['model'],
                'model_code': res['model_code'],
                'invoice_policy': res['invoice_policy'],
                'purchase_method': res['purchase_method'],
                'inner_code': res['inner_code'],
                'segment': res['segment'] ,
                'fmpi_product': True,
                'run_by_sync': True,
                'write_date': res['fmpi_product_write_date']
              })
          else:
            logger.info("Skipping Part Number: (" + str(r) + ") "+ (res['name'] or '') + " has no changes.")
      conn.close()
    else:
      raise UserError(_("Connecting to FMPI Server has failed!"))

  @api.multi
  def action_sync_service(self):
    # set connection parameters to FMPI
    conn_string = "host='" + self.fmpi_host + \
      "' dbname='"+ self.fmpi_pgn + \
      "' user='"+ self.fmpi_pgu + \
      "' password='"+ self.fmpi_pgp + "'"
    logger.info("connecting to the database\n ->%s"%(conn_string))
    conn = psycopg2.connect(conn_string)
    if conn:
      cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
      # set upload string (SQL)
      logger.info("Executing FMPI Query....")
      cursor.execute("""SELECT * FROM product_template     
        WHERE sub_type = 'labor';""")
      result_set = cursor.fetchall()
      if(result_set):
        pt_obj = self.env['product.template']
        r = 0
        for res in result_set:
          r+=1
          logger.info("Checking existence of Labor Code: (" + str(r) + ") "+ (res['name'] or ''))
          ptr = pt_obj.search([('name','=',res['name'])])
          if not ptr:
            logger.info("Labor Code: (" + str(r) + ") "+ (res['name'] or '') + " does not exists!...creating new product_template")
            ptr.create({
              'name': res['name'],
              'description': res['description'],
              'description_sale': res['description_sale'],
              'description_picking': res['description_picking'],
              'description_pickingin': res['description_pickingin'],
              'description_pickingout': res['description_pickingout'],
              'type': res['type'],
              'sale_ok': res['sale_ok'],
              'purchase_ok': False,
              'sub_type': res['sub_type'],
              'categ_id': self.parts_categ_id.id,
              'list_price': res['list_price'],
              'model': res['model'],
              'model_code': res['model_code'],
              'inner_code': res['inner_code'],
              'segment': res['segment'],
              'fmpi_product': True,
              'fmpi_product_id': res['id'],
              'write_date': res['fmpi_product_write_date']
            })
          elif res['fmpi_product_write_date'] != ptr.write_date:
              logger.info("Labor Code: (" + str(r) + ") "+ (res['name'] or '') + " has changes. Updating...")
              ptr.write({
                'name': res['name'],
                'description': res['description'],
                'description_sale': res['description_sale'],
                'description_picking': res['description_picking'],
                'description_pickingin': res['description_pickingin'],
                'description_pickingout': res['description_pickingout'],
                'list_price': res['list_price'],
                'model': res['model'],
                'model_code': res['model_code'],
                'inner_code': res['inner_code'],
                'segment': res['segment'] ,
                'fmpi_product': True,
                'run_by_sync': True,
                'write_date': res['fmpi_product_write_date']
              })
          else:
            logger.info("Skipping Labor Code: (" + str(r) + ") "+ (res['name'] or '') + " has no changes.")
      conn.close()
    else:
      raise UserError(_("Connecting to FMPI Server has failed!"))

  @api.multi
  def action_sync_service_history(self):
    # set connection parameters to FMPI
    url = self.api_host.strip()
    db = self.fmpi_pgn
    username = self.api_user
    password = self.api_pass
    # attempt to connect
    logger.info("Connecting to "+url)
    common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if not uid:
      raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
      return 
    models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
    if not models:
      raise exceptions.except_orm(_('Models: Remote Authentication Failed'), _(url + " failed to authenticate " + username))
      return
    
    d_ids = self.env['fmpi.service.history'].search([(1,"=",1)]).ids
    if d_ids:
      
      s_ids = "'" + str(d_ids).replace("[","(").replace("]",")") + "'"
      logger.info("s_ids = " + s_ids)
      rec = models.execute_kw(db, uid, password,
        'fmpi.service.history', 'search',
        [['id','not in', s_ids]]
        )
      if rec:
        for r in rec:
          logger.info("FMPI Record ID:"+ str(r.id))
FasResCompany()