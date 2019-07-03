from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class ServiceTakttimeCancel(models.TransientModel):
    _name = "service.takttime.cancel"
    _description = "Service Takttime Cancel"

    name = fields.Text(string="Reason", required=True)

    @api.multi
    def action_cancel(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        ids = self._context.get('active_ids')
        if ids is None:
            return act_close
        assert len(ids) == 1, "Only 1 Order Line is expected"
        service_taktime_cancel = self.env['sale.order.line'].browse(ids)
        service_status_logs = "Cancel by: " + self.env.user.name + "\n" + \
                "Cancel at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
                "Cancel notes: " + (self.name or '') + "\n" + \
                "--------------------------------------------------\n"
        service_taktime_cancel.write({'service_status_logs': service_status_logs + (service_taktime_cancel.service_status_logs or '')})
        service_taktime_cancel.service_cancel()
        return act_close

ServiceTakttimeCancel()