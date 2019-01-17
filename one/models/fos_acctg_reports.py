from odoo import models, fields, api, exceptions, _
import logging

class FOSActgReports(models.Model):
    _name = "fos.acctg.reports"

@api.multi
def general_ledger_report(self):
    inet_host = self.env.user.company_id.inet_url
    dbname = self.env.user.company_id.dealer_pgn
    report_url = inet_host + "/" + dbname  + "/fos_sales_calculator_quotation.rpt&prompt0=" \
      + str(self.id) 
    return {
      'type' : 'ir.actions.act_url',
      'url':report_url,
      'target': 'new'
    }

FOSActgReports()