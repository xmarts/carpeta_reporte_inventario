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
        id_stock_gdl = self.env['stock.warehouse'].search([('code','=','GDL')], limit=1)
        id_stock_cdmx = self.env['stock.warehouse'].search([('code','=','CDMX')], limit=1)
        id_stock_mer = self.env['stock.warehouse'].search([('code','=','MER')], limit=1)

        obj_stock = self.env['stock.quant'].search([('code_product','=',self.default_code)])
        for line in obj_stock:
            if id_stock_gdl:
                if line.location_id.id == id_stock_gdl.lot_stock_id.id:
                    disponible = line.quantity - line.reserved_quantity
                    self.stock_gdl = disponible
            if id_stock_cdmx:
                if line.location_id.id == id_stock_cdmx.lot_stock_id.id:
                    disponible = line.quantity - line.reserved_quantity
                    self.stock_cdmx = disponible
            if id_stock_mer:
                if line.location_id.id == id_stock_mer.lot_stock_id.id:
                    disponible = line.quantity - line.reserved_quantity
                    self.stock_mer = disponible 

        obj_transito = self.env['stock.move.line'].search([('code_product_id','=',self.default_code)])
        id_vendor = self.env['stock.location'].search([('name','=','Vendors')], limit=1)
        for x in obj_transito:
            if x.location_id.id == id_vendor.id:
                if id_stock_gdl:
                    if x.location_dest_id.id == id_stock_gdl.lot_stock_id.id:
                        self.et_co = x.product_uom_qty
                if id_stock_cdmx:
                    if x.location_dest_id.id == id_stock_cdmx.lot_stock_id.id:
                        self.et_cc = x.product_uom_qty
                if id_stock_mer:
                    if x.location_dest_id.id == id_stock_mer.lot_stock_id.id:
                        self.et_cs = x.product_uom_qty


    