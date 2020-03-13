# -*- coding: utf-8 -*-

from odoo import models, fields, api


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

    @api.one
    def _compute(self):
        id_stock_gdl = self.env['stock.location'].search([('name','=','GDL')],limit=1)
        product = self.env['product.product'].search([('product_tmpl_id','=',self.id)])
        cont = 0
        
        #print(product.name,product.default_code)
        p1 = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',id_stock_gdl.id)])
        if p1:
            cont += p1.quantity

        #print("LOCATION :: PATH :: ",id_stock_gdl.parent_path)
        for x in id_stock_gdl.child_ids:
            p1 = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',x.id)])
            if p1:
                #print(p1.quantity)
                cont += p1.quantity
            for y in x.child_ids:
                p1 = self.env['stock.quant'].search([('product_id','=',product.id),('location_id','=',y.id)])
                if p1:
                    #print(p1.quantity)
                    cont += p1.quantity
        #print(product.name,cont)
        self.stock_gdl = cont-p1.reserved_quantity

        id_stock_cdmx = self.env['stock.location'].search([('name','=','CDMX')], limit=1)
        cdmxproduct=self.env['product.product'].search([('product_tmpl_id','=', self.id)])
        cdmxcount = 0

        p2 = self.env['stock.quant'].search([('product_id','=',cdmxproduct.id),('location_id','=',id_stock_cdmx.id)])
        if p2:
            cdmxcount += p2.quantity

        for cdmx in id_stock_cdmx.child_ids:
            p2 = self.env['stock.quant'].search([('product_id','=', cdmxproduct.id),('location_id','=',cdmx.id)])
            if p2:
                cdmxcount+=p2.quantity

            for cdy in cdmx.child_ids:
                p2=self.env['stock.quant'].search([('product_id','=',cdmxproduct.id),('location_id','=',cdy.id)])
                if p2:
                    cdmxcount +=p2.quantity
        self.stock_cdmx = cdmxcount-p2.reserved_quantity
        #print(cdmxproduct.name, cdmxcount)

        id_stock_mer = self.env['stock.location'].search([('name','=','MER')], limit=1)
        merproduct=self.env['product.product'].search([('product_tmpl_id','=', self.id)])
        mercount = 0

        p3 = self.env['stock.quant'].search([('product_id','=',merproduct.id),('location_id','=',id_stock_mer.id)])
        if p3:
            merproduct+=p3.quantity

        for merx in id_stock_mer.child_ids:
            p3= self.env['stock.quant'].search([('product_id','=',merproduct.id),('location_id','=',merx.id)])
            if p3:
                mercount+=p3.quantity

            for mery in merx.child_ids:
                p3=self.env['stock.quant'].search([('product_id','=',merproduct.id),('location_id','=',mery.id)])
                if p3:
                    mercount+=p3.quantity
            self.stock_mer=mercount-p3.reserved_quantity

        id_stockw_gdl = self.env['stock.warehouse'].search([('code','=','GDL')],limit=1)
        id_stockw_cdmx = self.env['stock.warehouse'].search([('code','=','CDMX')], limit=1)
        id_stockw_mer = self.env['stock.warehouse'].search([('code','=','MER')], limit=1)

        obj_transito = self.env['stock.move.line'].search([('code_product_id','=',self.default_code)])
        id_vendor = self.env['stock.location'].search([('name','=','Vendors')], limit=1)

        for x in obj_transito:
            if x.location_id.id == id_vendor.id:
                if id_stockw_gdl:
                    if x.location_dest_id.id == id_stockw_gdl.lot_stock_id.id:
                        self.et_co = x.product_uom_qty
                if id_stockw_cdmx:
                    if x.location_dest_id.id == id_stockw_cdmx.lot_stock_id.id:
                        self.et_cc = x.product_uom_qty
                if id_stockw_mer:
                    if x.location_dest_id.id == id_stockw_mer.lot_stock_id.id:
                        self.et_cs = x.product_uom_qty


    