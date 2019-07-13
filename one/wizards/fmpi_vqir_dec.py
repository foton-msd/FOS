from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class FmpiVqirDec(models.TransientModel):
    _name = "fmpi.vqir.dec"
    _description = "FMPI - VQIR Returned Notes"

    name = fields.Text(string="Returned Notes", required=True)

    @api.multi
    def action_dec(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        ids = self._context.get('active_ids')
        if ids is None:
            return act_close
        assert len(ids) == 1, "Only 1 VQIR is expected"
        fmpi_vqir_obj = self.env['fmpi.vqir'].browse(ids)
        if fmpi_vqir_obj.vqir_state == 'ack':
            vqir_state_logs = "Document:" + fmpi_vqir_obj.name + "\n" + \
                "Returned by: " + self.env.user.name + "\n" + \
                "Returned at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
                "Returned notes: " + (self.name or '') + "\n" + \
                "--------------------------------------------------\n"
            fmpi_vqir_obj.write({'vqir_state': 'declined',
                'vqir_state_logs': vqir_state_logs + (fmpi_vqir_obj.vqir_state_logs or '')})
            fmpi_vqir_obj.action_dec_api()
        else:
            raise UserError(_("You cannot Returned this VQIR in this state"))
        return act_close

FmpiVqirDec()