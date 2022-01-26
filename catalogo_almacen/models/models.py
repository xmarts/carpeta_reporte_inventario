# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = "stock.quant"

    code_product = fields.Char(related="product_id.default_code", string="Código del producto")

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    code_product_id = fields.Char(related="product_id.default_code", string="Código del producto")

class ProductInstallationType(models.Model):
    _name = 'product.installation.type'

    name = fields.Char(string="Tipo Instalacion")

class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_gdl = fields.Integer(string="Cedis occidente", compute="_compute")
    et_co = fields.Integer(string="En tránsito CO", compute="_compute")
    stock_cdmx = fields.Integer(string="Cedis centro", compute="_compute")
    et_cc = fields.Integer(string="En tránsito CC", compute="_compute")
    stock_mer = fields.Integer(string="Cedis sur", compute="_compute")
    et_cs = fields.Integer(string="En tránsito CS", compute="_compute")
    product_installation_type_id = fields.Many2one('product.installation.type', string='Tipo de instalacion')

    def _compute(self):
        for rec in self:
            id_stock_gdl = self.env['stock.location'].search([('name','=','GDL')],limit=1)
            id_stock_cdmx = self.env['stock.location'].search([('name','=','CDMX')],limit=1)
            id_stock_mer = self.env['stock.location'].search([('name','=','MER')],limit=1)

            products = self.env['product.product'].search([('product_tmpl_id','=',rec.id)])
            for product in products:
                print("Linea ----- ", product.id)
                sq_gdl = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',id_stock_gdl.id)])
                if sq_gdl:
                    rec.stock_gdl += sq_gdl.quantity

                for x in id_stock_gdl.child_ids:
                    sq_gdl = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',x.id)])
                    if sq_gdl:
                        rec.stock_gdl += sq_gdl.quantity
                    for y in x.child_ids:
                        sq_gdl = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',y.id)])
                        if sq_gdl:
                            rec.stock_gdl += sq_gdl.quantity

                product_sq_cdmx = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',id_stock_cdmx.id)])
                if product_sq_cdmx:
                    rec.stock_cdmx += product_sq_cdmx.quantity

                for x in id_stock_cdmx.child_ids:
                    product_sq_cdmx = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',x.id)])
                    if product_sq_cdmx:
                        rec.stock_cdmx += product_sq_cdmx.quantity
                    for y in x.child_ids:
                        product_sq_cdmx = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',y.id)])
                        if product_sq_cdmx:
                            rec.stock_cdmx += product_sq_cdmx.quantity

                product_sq_mer = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',id_stock_mer.id)])
                if product_sq_mer:
                    rec.stock_mer += product_sq_mer.quantity

                for x in id_stock_mer.child_ids:
                    product_sq_mer = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',x.id)])
                    if product_sq_mer:
                        rec.stock_mer += product_sq_mer.quantity
                    for y in x.child_ids:
                        product_sq_mer = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',y.id)])
                        if product_sq_mer:
                            rec.stock_mer += product_sq_mer.quantity

                product_reserved = self.env['stock.picking'].search([('state','in',['assigned']),('picking_type_code','=','outgoing')])
                product_reserved_lines = self.env['stock.move'].search([('product_id','=',product.id),('picking_id','in',product_reserved.ids)])

                for x in product_reserved_lines:
                    for y in x.tiempo_entrega_tabla:
                        if y.cedis_selection == 'occidente':
                            rec.stock_gdl -= x.reserved_availability
                        if y.cedis_selection == 'centro':
                            rec.stock_cdmx -= x.reserved_availability
                        if y.cedis_selection == 'sur':
                            rec.stock_mer -= x.reserved_availability

                if rec.stock_gdl < 0:
                    rec.stock_gdl = 0
                if rec.stock_cdmx < 0:
                    rec.stock_cdmx = 0
                if rec.stock_mer < 0:
                    rec.stock_mer = 0

                product_purchase= self.env['stock.picking'].search([('state','in',['confirmed','assigned']),('picking_type_code','=','incoming')])
                product_purchase_lines = self.env['stock.move'].search([('product_id','=',product.id),('picking_id','in',product_purchase.ids)])

                for x in product_purchase_lines:
                    if x.picking_id.location_dest_id.location_id.name == 'GDL':
                        rec.et_co += x.product_uom_qty
                    if x.picking_id.location_dest_id.location_id.name == 'CDMX':
                        rec.et_cc += x.product_uom_qty
                    if x.picking_id.location_dest_id.location_id.name == 'MER':
                        rec.et_cs += x.product_uom_qty

                product_sale= self.env['stock.picking'].search([('state','in',['confirmed','assigned']),('picking_type_code','=','outgoing')])
                product_sale_lines = self.env['stock.move'].search([('product_id','=',product.id),('picking_id','in',product_sale.ids)])

                for x in product_sale_lines:
                    for y in x.tiempo_entrega_tabla:
                        if y.cedis_selection == 'occidente':
                            rec.et_co -= (x.product_uom_qty - x.reserved_availability)
                    for y in x.tiempo_entrega_tabla:
                        if y.cedis_selection == 'centro':
                            rec.et_cc -= (x.product_uom_qty - x.reserved_availability)
                    for y in x.tiempo_entrega_tabla:
                        if y.cedis_selection == 'sur':
                            rec.et_cs -= (x.product_uom_qty - x.reserved_availability)

                if rec.et_co < 0:
                    rec.et_co = 0
                if rec.et_cc < 0:
                    rec.et_cc = 0
                if rec.et_cs < 0:
                    rec.et_cs = 0