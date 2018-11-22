from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class RepairOrder(models.Model):
    _name = "fos.repair.orders"
    _description = "Repair Orders"

    name = fields.Char(string="R.O. Number", readonly=True, default="auto-generated")
    date = fields.Datetime(string="Date", default=lambda self: fields.datetime.now(), required=True)
    customer_id = fields.Many2one(string="Customer", comodel_name="res.partner", required=True)
    fu_id = fields.Many2one(string="FOTON Number", comodel_name="one.fu", required=True)
    fu_chassis_number = fields.Char(string="Chassis Number", related="fu_id.chassis_number", readonly=True)
    fu_engine_number = fields.Char(string="Engine Number", related="fu_id.engine_number", readonly=True)
    fu_conduction_sticker = fields.Char(string="Conduction Sticker", related="fu_id.conduction_sticker", readonly=True)
    fu_plate_number = fields.Char(string="Plate Number", related="fu_id.plate_number", readonly=False)
    fu_local_name = fields.Char(string="Local Name", related="fu_id.fmpi_fu_local_name_id.name", readonly=True)
    service_advisor_id = fields.Many2one(string="Service Advisor", comodel_name="res.users", 
        required=True, domain=lambda self: [( "groups_id", "=", self.env.ref( "one.group_service_advisors" ).id )] )
    state = fields.Selection(string="Status", selection=[("draft","Draft"),("confirm","Confirmed"),("cancel","Cancelled")], default="draft")
    run_km = fields.Integer(string="Run KM")
    ro_lines = fields.One2many(string="Repair Order Lines", 
        comodel_name="fos.repair.order.lines", inverse_name="ro_id", ondelete="cascade")
    estimate_id = fields.Many2one(string="Estimate Number", comodel_name="sale.order", copy=False)
    cancel_reason = fields.Text("Reason for cancellation", readonly=True, copy=False)
    prepared_by_id = fields.Many2one(string="Prepared by", comodel_name="res.users", default=lambda self: self.env.user, readonly=True)
    prepared_by_desig = fields.Char(string="Designation", related="prepared_by_id.partner_id.function", readonly=True)

    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('fos.ro.seq')
        result = super(RepairOrder, self).create(vals)
        return result
    
    @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})
    
    @api.multi
    def action_confirm(self):
        notes = ""
        for lines in self.ro_lines:
            notes += lines.name + "\n"
        so_obj = self.env['sale.order']
        self.ensure_one()        
        new_so = so_obj.create({
            'partner_id': self.customer_id.id,
            'date_order': fields.datetime.now(),
            'fu_id': self.fu_id.id,
            'so_type': 'service',
            'run_km': self.run_km,
            'note': notes,
            'repair_order_id': self.id
        })
        if new_so:            
            return self.write({'state': 'confirm', 'estimate_id': new_so.id})

RepairOrder()

class RepairOrderLines(models.Model):
    _name = "fos.repair.order.lines"
    _description = "Repair Orders"

    name = fields.Text(string="Description", required=True)
    ro_id = fields.Many2one(string="R.O. Number", comodel_name="fos.repair.orders")
RepairOrderLines()