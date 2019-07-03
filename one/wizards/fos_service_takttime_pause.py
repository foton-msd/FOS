from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class ServiceTakttimePause(models.TransientModel):
    _name = "service.takttime.pause"
    _description = "Service Takttime Pause"

    name = fields.Text(string="Reason", required=True)

    @api.multi
    def action_pause(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        ids = self._context.get('active_ids')
        if ids is None:
            return act_close
        assert len(ids) == 1, "Only 1 Order Line is expected"
        service_taktime_pause = self.env['sale.order.line'].browse(ids)
        service_status_logs = "Paused by: " + self.env.user.name + "\n" + \
                "Pause at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
                "Pause notes: " + (self.name or '') + "\n" + \
                "--------------------------------------------------\n"
        service_taktime_pause.write({'service_status_logs': service_status_logs + (service_taktime_pause.service_status_logs or '')})
        service_taktime_pause.service_pause()
        return act_close

ServiceTakttimePause()