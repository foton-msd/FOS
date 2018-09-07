from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FosCancelRO(models.TransientModel):
    _name = "fos.cancel.ro"
    _description = "Cancelled Repair Orders Reason"

    name = fields.Text(string="Reason of cancellation", required=True)

    @api.multi
    def action_cancel(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        ids = self._context.get('active_ids')
        if ids is None:
            return act_close
        assert len(ids) == 1, "Only 1 Repair Order is expected"
        ro = self.env['fos.repair.orders'].browse(ids)
        ro.cancel_reason = self.name
        if ro.state == 'draft':
            ro.action_cancel()
        else:
            raise UserError(_("You cannot cancel R.O. in this state"))
        return act_close

FosCancelRO()