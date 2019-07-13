from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class FmpiVqirPd(models.TransientModel):
    _name = "fmpi.vqir.pd"
    _description = "FMPI - VQIR Paid Notes"

    name = fields.Text(string="Paid Notes", required=True)

    @api.multi
    def action_pd(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        ids = self._context.get('active_ids')
        if ids is None:
            return act_close
        assert len(ids) == 1, "Only 1 VQIR is expected"
        fmpi_vqir_obj = self.env['fmpi.vqir'].browse(ids)
        if fmpi_vqir_obj.vqir_state in ['approved','preclaimed']:
            vqir_state_logs = "Document:" + fmpi_vqir_obj.name + "\n" + \
                "Set as Paid by: " + self.env.user.name + "\n" + \
                "Set as Paid at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
                "Paid notes: " + (self.name or '') + "\n" + \
                "--------------------------------------------------\n"
            fmpi_vqir_obj.write({'vqir_state': 'paid',
                'vqir_state_logs': vqir_state_logs + (fmpi_vqir_obj.vqir_state_logs or '')})
            fmpi_vqir_obj.action_pd_api()
        else:
            raise UserError(_("You cannot pay this VQIR in this state"))
        return act_close

FmpiVqirPd()