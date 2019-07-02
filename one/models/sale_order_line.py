# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.addons import decimal_precision as dp
import logging
logger = logging.getLogger(__name__)

class FasSaleOrderLine(models.Model):
  _inherit = 'sale.order.line'

  charged_to = fields.Selection(string="Charged to", required=True,
    selection=[('warranty','Warranty'),
      ('customer','Customer'),
      ('internal','Internal'),
      ('first_pms','First PMS'),
      ('tsb','TSB'),
      ('add-on-costs','Add-On-Costs')])
  fu_id = fields.Many2one(string="FOTON Number", comodel_name="one.fu")
  discount_amount = fields.Float(string="Discount (Amount)", digits=dp.get_precision('Discount'))
  part_number = fields.Many2one(string="Part Number", comodel_name="product.product")
  parts_and_jobs = fields.Many2one(string="Parts & Labor", comodel_name="product.product")
  parts_and_job_sub_type = fields.Selection(string="Sub-type", selection=[('units','Units'),('parts','Parts'),('supplies','Supplies'),('labor','Labor'),('merchandise','Merchandise'),('addons','Addons')], related="parts_and_jobs.product_tmpl_id.sub_type")
  units_and_addons = fields.Many2one(string="Units & Addons", comodel_name="product.product")
  part_desc = fields.Text(string="Parts Description", related="product_id.product_tmpl_id.description_sale", readonly=True)
  service_technicians = fields.One2many(string="Technicians", comodel_name="fos.service.technician", inverse_name="order_line_id")
  service_start_date = fields.Datetime(string="Actual Start", readonly=True)
  service_end_date = fields.Datetime(string="Actual End", readonly=True)
  service_duration = fields.Float(
        'Real Duration', compute='_compute_duration',
        readonly=True, store=False)
  service_status = fields.Selection(string="Status", readonly=True, copy=False, selection=[
      ('start', 'Started'),
      ('pause', 'Paused'),
      ('cancel', 'Cancelled'),
      ('finish', 'Finished')])
  service_time_ids = fields.One2many('sale.order.line.takt', 'order_line_id')

  @api.one
  @api.depends('service_time_ids.duration')
  def _compute_duration(self):
    self.service_duration = sum(self.service_time_ids.mapped('duration'))

  @api.multi
  def service_start(self):
      self.ensure_one()
      # Need a loss in case of the real time exceeding the expected
      timeline = self.env['sale.order.line.takt']
      if self.service_duration <= 0:
          loss_id = self.env['fos.productivity.losses'].search([('loss_type','=','productive')], limit=1)
          if not len(loss_id):
              raise UserError(_("You need to define at least one productivity loss in the category 'Productivity'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
      else:
          loss_id = self.env['fos.productivity.losses'].search([('loss_type','=','performance')], limit=1)
          if not len(loss_id):
              raise UserError(_("You need to define at least one productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
      for workorder in self:
          timeline.create({
              'order_line_id': workorder.id,
              'description': _('Time Tracking: ')+self.env.user.name,
              'loss_id': loss_id[0].id,
              'date_start': datetime.now(),
              'user_id': self.env.user.id
          })
      return self.write({'service_status': 'start',
                  'date_start': datetime.now(), 'service_start_date': datetime.now(),
      })

  @api.multi
  def service_pause(self):
    self.end_previous()
    return self.write({'service_status': 'pause'})

  @api.multi
  def end_previous(self):
      timeline_obj = self.env['sale.order.line.takt']
      domain = [('order_line_id', 'in', self.ids), ('date_end', '=', False)]
      domain.append(('user_id', '=', self.env.user.id))
      not_productive_timelines = timeline_obj.browse()
      for timeline in timeline_obj.search(domain, limit=1):
          wo = timeline.order_line_id
          maxdate = fields.Datetime.from_string(timeline.date_start) #+ relativedelta(minutes=wo.duration_expected - wo.duration)
          enddate = datetime.now()
          if maxdate > enddate:
            timeline.write({'date_end': enddate})
          else:
            timeline.write({'date_end': maxdate})
            not_productive_timelines += timeline.copy({'date_start': maxdate, 'date_end': enddate})
      if not_productive_timelines:
          loss_id = self.env['fos.productivity.losses'].search([('loss_type', '=', 'performance')], limit=1)
          if not len(loss_id):
              raise UserError(_("You need to define at least one unactive productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
          not_productive_timelines.write({'loss_id': loss_id.id})
      return True

  @api.multi
  def service_cancel(self):
    return self.write({'service_status': 'cancel'})

  @api.one
  def service_finish(self):
    self.end_previous()
    self.service_status = "finish"
    self.service_end_date = datetime.now()

  @api.onchange("discount_amount")  
  def DiscountAmountChanged(self):    
    if self.price_unit:
      self.discount = (self.discount_amount / (self.price_unit * self.product_uom_qty)) * 100    

  @api.onchange("discount")  
  def DiscountPercentChanged(self):    
    if self.price_unit:
      self.discount_amount = (self.product_uom_qty * self.price_unit) * (self.discount / 100)

  @api.onchange("part_number")
  @api.depends("product_id")
  def OnChangedPartNumber(self):
    self.product_id = self.part_number
    self.product_id_change()

  @api.onchange("parts_and_jobs")
  @api.depends("product_id")
  def OnChangedPartsAndLabor(self):
     self.product_id = self.parts_and_jobs
     self.product_id_change()

  @api.onchange("units_and_addons")
  @api.depends("product_id")
  def OnChangedUnitsAndAddons(self):
    self.product_id = self.units_and_addons
    self.product_id_change()

  @api.multi
  def name_get(self):
    result = []
    for so_line in self:
      result.append((so_line.id, '[%s] %s' % (so_line.order_id.name, so_line.order_id.partner_id.name)))
    return result

FasSaleOrderLine()

class FosTaktTime(models.Model):
    _name = "sale.order.line.takt"
    _description = "Takt Time"
    _order = "id desc"

    order_line_id = fields.Many2one('sale.order.line', 'Order Line')
    user_id = fields.Many2one(
        'res.users', "User",
        default=lambda self: self.env.uid)
    loss_id = fields.Many2one(
        'fos.productivity.losses', "Loss Reason",
        ondelete='restrict', required=True)
    loss_type = fields.Selection(
        "Effectiveness", related='loss_id.loss_type', store=True)
    description = fields.Text('Reason')
    date_start = fields.Datetime('Start Date', default=fields.Datetime.now, required=True)
    date_end = fields.Datetime('End Date')
    duration = fields.Float('Duration', compute='_compute_duration', store=False)

    @api.depends('date_end', 'date_start')
    def _compute_duration(self):
        for blocktime in self:
            if blocktime.date_end:
                d1 = fields.Datetime.from_string(blocktime.date_start)
                d2 = fields.Datetime.from_string(blocktime.date_end)
                diff = d2 - d1
                blocktime.duration = round(diff.total_seconds() / 60.0, 2)
            else:
                blocktime.duration = 0.0
FosTaktTime()
