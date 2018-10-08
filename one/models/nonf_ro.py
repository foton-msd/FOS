from odoo import models, fields, api
import logging
logger = logging.getLogger(__name__)

class NonFRepairOrder(models.Model):
    _name = "nonf.ro"
    _description = "Non-FOTON - Repair Orders"

    name = fields.Char(string="R.O. Number", readonly=True, default="auto-generated")
    date = fields.Datetime(string="Date", default=lambda self: fields.datetime.now(), required=True)
    customer_id = fields.Many2one(string="Customer", comodel_name="res.partner", required=True)
    nonf_unit_id = fields.Many2one(string="Plate Number", comodel_name="nonf.units", required=True)
    chassis_number = fields.Char(string="Chassis Number", related="nonf_unit_id.chassis_number")
    engine_number = fields.Char(string="Engine Number", related="nonf_unit_id.engine_number")
    conduction_sticker = fields.Char(string="Conduction Sticker", related="nonf_unit_id.conduction_sticker")
    plate_number = fields.Char(string="Plate Number", related="nonf_unit_id.name")
    owner_name = fields.Char(string="Registered to", related="nonf_unit_id.owner_name")
    maker_id = fields.Char(string="Make", related="nonf_unit_id.maker_id.name")
    model_id = fields.Char(string="Model", related="nonf_unit_id.model_id.name")
    service_advisor_id = fields.Many2one(string="Service Advisor", comodel_name="res.users", 
        required=True, domain=lambda self: [( "groups_id", "=", self.env.ref( "one.group_service_advisors" ).id )] )
    state = fields.Selection(string="Status", selection=[("draft","Draft"),("confirm","Confirmed"),("cancel","Cancelled")], default="draft")
    run_km = fields.Integer(string="Run KM")
    ro_lines = fields.One2many(string="Repair Order Lines", 
        comodel_name="nonf.ro.lines", inverse_name="ro_id", ondelete="cascade")
    estimate_id = fields.Many2one(string="Estimate Number", comodel_name="sale.order", copy=False)
    cancel_reason = fields.Text("Reason for cancellation", readonly=True, copy=False)
    prepared_by_id = fields.Many2one(string="Prepared by", comodel_name="res.users", default=lambda self: self.env.user, readonly=True)
    prepared_by_desig = fields.Char(string="Designation", related="prepared_by_id.partner_id.function", readonly=True)

    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('nonf.ro.seq')
        result = super(NonFRepairOrder, self).create(vals)
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
            'nonf_unit_id': self.nonf_unit_id.id,
            'so_type': 'service2',
            'run_km': self.run_km,
            'note': notes,
            'nonf_ro_id': self.id
        })
        if new_so:            
            return self.write({'state': 'confirm', 'estimate_id': new_so.id})

NonFRepairOrder()

class NonFRepairOrderLines(models.Model):
    _name = "nonf.ro.lines"
    _description = "Non-FOTON Repair Order Lines"

    name = fields.Text(string="Description", required=True)
    ro_id = fields.Many2one(string="R.O. Number", comodel_name="nonf.ro")

NonFRepairOrderLines()