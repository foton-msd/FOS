from xmlrpc import client as xmlrpclib
from odoo import models, fields, api, exceptions, _
import logging
logger = logging.getLogger(__name__)

class SyncPartsMaster(models.Model):
    _inherit = "res.company"
    
    @api.multi
    def sync_parts_master(self):
        url = self.fmpi_host.strip()
        db = self.fmpi_pgn
        username = self.fmpi_pgu
        password = self.fmpi_pgp
        # attempt to connect
        logger.info("Connecting to "+url)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        if not uid:
            raise exceptions.except_orm(_('Remote Authentication Failed'), _(url + " failed to authenticate " + username))
            return 
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            
        # get entire parts master from product_template
        fmpi_pts = models.execute_kw(db, uid, password,
            'product.template', 'search_read',[[('sub_type','=','parts')]], 
            {'fields': ['id','write_date']})
        if fmpi_pts:
            dealer_pt_obj = self.env['product.template']
            for fmpi_pt in fmpi_pts:
                logger.info("Searching FMPI ID " +  str(fmpi_pt['id']) + " from " + str(self.env.cr.dbname))
                dealer_pts = self.env['product.template'].search([('fmpi_product_id', 'in', [fmpi_pt['id']])])
                if not dealer_pts:
                    logger.info("New Template from FMPI...")
                    fmpi_pt_full_detail = models.execute_kw(db, uid, password,
                        'product.template', 'search_read',[[['id','=',fmpi_pt['id']]]])
                    if fmpi_pt_full_detail:
                        values = {
                            'name': fmpi_pt_full_detail[0]['name'],
                            'description': fmpi_pt_full_detail[0]['description'],
                            'description_sale': fmpi_pt_full_detail[0]['description_sale'],
                            'description_purchase': fmpi_pt_full_detail[0]['description_purchase'],
                            'type': fmpi_pt_full_detail[0]['type'],
                            'list_price': fmpi_pt_full_detail[0]['list_price'],
                            'standard_price': fmpi_pt_full_detail[0]['dnp'] or 0,
                            'sub_type': fmpi_pt_full_detail[0]['sub_type'],
                            'categ_id': self.parts_categ_id.id,                             
                            'volume': fmpi_pt_full_detail[0]['volume'],
                            'weight': fmpi_pt_full_detail[0]['weight'],                                    
                            'sale_ok': fmpi_pt_full_detail[0]['sale_ok'],
                            'purchase_ok': fmpi_pt_full_detail[0]['purchase_ok'],
                            'active': fmpi_pt_full_detail[0]['active'],
                            'default_code': fmpi_pt_full_detail[0]['default_code'] or '',
                            'sale_delay': fmpi_pt_full_detail[0]['sale_delay'],
                            'tracking': fmpi_pt_full_detail[0]['tracking'],
                            'description_picking': fmpi_pt_full_detail[0]['description_picking'] or '',
                            'description_pickingout': fmpi_pt_full_detail[0]['description_pickingout'] or '',
                            'description_pickingin': fmpi_pt_full_detail[0]['description_pickingin'] or '',
                            'service_type': fmpi_pt_full_detail[0]['service_type'] or '',
                            'sale_line_warn': fmpi_pt_full_detail[0]['sale_line_warn'] or '',
                            'sale_line_warn_msg': fmpi_pt_full_detail[0]['sale_line_warn_msg'] or '',
                            'expense_policy': fmpi_pt_full_detail[0]['expense_policy'] or '',
                            'invoice_policy': fmpi_pt_full_detail[0]['invoice_policy'] or '',
                            'purchase_method': fmpi_pt_full_detail[0]['purchase_method'] or '',
                            'purchase_line_warn': fmpi_pt_full_detail[0]['purchase_line_warn'] or '',
                            'purchase_line_warn_msg': fmpi_pt_full_detail[0]['purchase_line_warn_msg'] or '',
                            'isc': fmpi_pt_full_detail[0]['isc'] or 0,
                            'fob_php': fmpi_pt_full_detail[0]['fob_php'] or 0,
                            'fob_usd': fmpi_pt_full_detail[0]['fob_usd'] or 0,
                            'fob_rmb': fmpi_pt_full_detail[0]['fob_rmb'] or 0,
                            'dnp': 0,
                            'loc1': fmpi_pt_full_detail[0]['loc1'] or '',
                            'loc2': fmpi_pt_full_detail[0]['loc2'] or '',
                            'loc3': fmpi_pt_full_detail[0]['loc3'] or '',
                            'loc4': fmpi_pt_full_detail[0]['loc4'] or '',
                            'loc5': fmpi_pt_full_detail[0]['loc5'] or '',
                            'loc6': fmpi_pt_full_detail[0]['loc6'] or '',
                            'loc7': fmpi_pt_full_detail[0]['loc7'] or '',
                            'loc8': fmpi_pt_full_detail[0]['loc8'] or '',
                            'loc9': fmpi_pt_full_detail[0]['loc9'] or '',
                            'model': fmpi_pt_full_detail[0]['model'] or '',
                            'model_code': fmpi_pt_full_detail[0]['model_code'] or '',
                            'inner_code': fmpi_pt_full_detail[0]['inner_code'] or '',
                            'segment': fmpi_pt_full_detail[0]['segment'] or '',
                            'fmpi_product_write_date': fmpi_pt_full_detail[0]['write_date'],                                
                            'no_of_hours': fmpi_pt_full_detail[0]['no_of_hours'] or 0,
                            'run_by_sync': True,
                            'fmpi_product': True,
                            'fmpi_product_id': fmpi_pt_full_detail[0]['id']
                                }
                        self.env['product.template'].create(values)
                else:
                    for dealer_pt in dealer_pts:
                        logger.info("Checking Part Number: " + dealer_pt.name)
                        if fmpi_pt['write_date'] == dealer_pt[0]['fmpi_product_write_date']:
                            logger.info("Nothing changed on ID "+ str(fmpi_pt['id']) + " skipping...")
                        else:
                            # update dealer's product_template
                            logger.info("FMPI's " + str(fmpi_pt['id']) + " has changed. Updating...")
                            # get full details from FMPI
                            fmpi_pt_full_detail = models.execute_kw(db, uid, password,
                                'product.template', 'search_read',[[['id','=',dealer_pt[0]['fmpi_product_id']]]])
                            if fmpi_pt_full_detail:
                                values = {
                                    'name': fmpi_pt_full_detail[0]['name'],
                                    'description': fmpi_pt_full_detail[0]['description'],
                                    'description_sale': fmpi_pt_full_detail[0]['description_sale'],
                                    'description_purchase': fmpi_pt_full_detail[0]['description_purchase'],
                                    'type': fmpi_pt_full_detail[0]['type'],
                                    'list_price': fmpi_pt_full_detail[0]['list_price'], 
                                    'sub_type': fmpi_pt_full_detail[0]['sub_type'],
                                    'categ_id': self.parts_categ_id.id,
                                    'standard_price': fmpi_pt_full_detail[0]['dnp'] or 0,                                   
                                    'volume': fmpi_pt_full_detail[0]['volume'],
                                    'weight': fmpi_pt_full_detail[0]['weight'],                                    
                                    'sale_ok': fmpi_pt_full_detail[0]['sale_ok'],
                                    'purchase_ok': fmpi_pt_full_detail[0]['purchase_ok'],
                                    'active': fmpi_pt_full_detail[0]['active'],
                                    'default_code': fmpi_pt_full_detail[0]['default_code'] or '',
                                    'sale_delay': fmpi_pt_full_detail[0]['sale_delay'],
                                    'tracking': fmpi_pt_full_detail[0]['tracking'],
                                    'description_picking': fmpi_pt_full_detail[0]['description_picking'] or '',
                                    'description_pickingout': fmpi_pt_full_detail[0]['description_pickingout'] or '',
                                    'description_pickingin': fmpi_pt_full_detail[0]['description_pickingin'] or '',
                                    'service_type': fmpi_pt_full_detail[0]['service_type'] or '',
                                    'sale_line_warn': fmpi_pt_full_detail[0]['sale_line_warn'] or '',
                                    'sale_line_warn_msg': fmpi_pt_full_detail[0]['sale_line_warn_msg'] or '',
                                    'expense_policy': fmpi_pt_full_detail[0]['expense_policy'] or '',
                                    'invoice_policy': fmpi_pt_full_detail[0]['invoice_policy'] or '',
                                    'purchase_method': fmpi_pt_full_detail[0]['purchase_method'] or '',
                                    'purchase_line_warn': fmpi_pt_full_detail[0]['purchase_line_warn'] or '',
                                    'purchase_line_warn_msg': fmpi_pt_full_detail[0]['purchase_line_warn_msg'] or '',
                                    'isc': fmpi_pt_full_detail[0]['isc'] or 0,
                                    'fob_php': fmpi_pt_full_detail[0]['fob_php'] or 0,
                                    'fob_usd': fmpi_pt_full_detail[0]['fob_usd'] or 0,
                                    'fob_rmb': fmpi_pt_full_detail[0]['fob_rmb'] or 0,
                                    'dnp': 0,
                                    'loc1': fmpi_pt_full_detail[0]['loc1'] or '',
                                    'loc2': fmpi_pt_full_detail[0]['loc2'] or '',
                                    'loc3': fmpi_pt_full_detail[0]['loc3'] or '',
                                    'loc4': fmpi_pt_full_detail[0]['loc4'] or '',
                                    'loc5': fmpi_pt_full_detail[0]['loc5'] or '',
                                    'loc6': fmpi_pt_full_detail[0]['loc6'] or '',
                                    'loc7': fmpi_pt_full_detail[0]['loc7'] or '',
                                    'loc8': fmpi_pt_full_detail[0]['loc8'] or '',
                                    'loc9': fmpi_pt_full_detail[0]['loc9'] or '',
                                    'model': fmpi_pt_full_detail[0]['model'] or '',
                                    'model_code': fmpi_pt_full_detail[0]['model_code'] or '',
                                    'inner_code': fmpi_pt_full_detail[0]['inner_code'] or '',
                                    'segment': fmpi_pt_full_detail[0]['segment'] or '',
                                    'fmpi_product_write_date': fmpi_pt_full_detail[0]['write_date'],                                
                                    'no_of_hours': fmpi_pt_full_detail[0]['no_of_hours'] or 0,
                                    'run_by_sync': True,
                                    'fmpi_product': True
                                }
                                dealer_pt.write(values)
                                
                                
SyncPartsMaster()