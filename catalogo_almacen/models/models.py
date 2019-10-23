# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"

    code_product = fields.Char(related="product_id.default_code", string="Código del producto")

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    code_product_id = fields.Char(related="product_id.default_code", string="Código del producto")

class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_gdl = fields.Integer(string="Cedis occidente", compute="_compute")
    et_co = fields.Integer(string="En tránsito CO", compute="_compute")
    stock_cdmx = fields.Integer(string="Cedis centro", compute="_compute")
    et_cc = fields.Integer(string="En tránsito CC", compute="_compute")
    stock_mer = fields.Integer(string="Cedis sur", compute="_compute")
    et_cs = fields.Integer(string="En tránsito CS", compute="_compute")

    @api.one
    def _compute(self):
        obj_stock = self.env['stock.quant'].search([('code_product','=',self.default_code)])
        for line in obj_stock:
            if line.location_id.id == 12:
                disponible = line.quantity - line.reserved_quantity
                self.stock_gdl = disponible
            if line.location_id.id == 19:
                disponible = line.quantity - line.reserved_quantity
                self.stock_cdmx = disponible
            if line.location_id.id == 25:
                disponible = line.quantity - line.reserved_quantity
                self.stock_mer = disponible 

        obj_transito = self.env['stock.move.line'].search([('code_product_id','=',self.default_code)])
        for x in obj_transito:
            if x.location_id.id == 8:
                if x.location_dest_id.id == 12:
                    self.et_co = x.product_uom_qty
                if x.location_dest_id.id == 19:
                    self.et_cc = x.product_uom_qty
                if x.location_dest_id.id == 25:
                    self.et_cs = x.product_uom_qty

    