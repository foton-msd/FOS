# -*- coding: utf-8 -*-
from odoo import http

# class Fas11(http.Controller):
#     @http.route('/fas11/fas11/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fas11/fas11/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fas11.listing', {
#             'root': '/fas11/fas11',
#             'objects': http.request.env['fas11.fas11'].search([]),
#         })

#     @http.route('/fas11/fas11/objects/<model("fas11.fas11"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fas11.object', {
#             'object': obj
#         })