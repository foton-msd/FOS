from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime

class FmpiVqirAck(models.TransientModel):
    _name = "fmpi.vqir.ack"
    _description = "FMPI - VQIR Acknowledgement Notes"

    name = fields.Text(string="Acknowledgement Notes")

    @api.multi
    def action_ack(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        ids = self._context.get('active_ids')
        if ids is None:
            return act_close
        assert len(ids) == 1, "Only 1 VQIR is expected"
        fmpi_vqir_obj = self.env['fmpi.vqir'].browse(ids)
        if fmpi_vqir_obj.vqir_state == 'submit':
            vqir_state_logs = "Document:" + fmpi_vqir_obj.name + "\n" + \
                "Acknowledged by: " + self.env.user.name + "\n" + \
                "Acknowledged at: " + datetime.datetime.now().strftime("%m/%d/%Y") + "\n" + \
                "Acknowledgement notes: " + (self.name or '') + "\n" + \
                "--------------------------------------------------\n"
            fmpi_vqir_obj.write({'vqir_state': 'ack',
                'vqir_state_logs': vqir_state_logs + (fmpi_vqir_obj.vqir_state_logs or '')})
            fmpi_vqir_obj.action_ack_api()
        else:
            raise UserError(_("You cannot acknowledge this VQIR in this state"))
        return act_close

FmpiVqirAck()