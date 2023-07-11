# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

_logger = logging.getLogger(__name__)


class UpdateRecipeProduct(models.TransientModel):
    _name = "recipe.product.wizard"
    _description = "Update Recipe Product"


    recipe_product_id = fields.Many2one('product.template',string='Recipe Product', required=True, domain=[('type','=','service'),('is_recipe','=',True)])
    is_recipe = fields.Boolean('Is Recipe')
    recipe_product_ids = fields.One2many('recipe.product.wizard.line','parent_id', string='Products')
    # recipe_product_ids = fields.Many2many('recipe.structure', string='Products')
    
    @api.onchange('recipe_product_id')
    def onchange_recipe_product(self):
        self.recipe_product_ids = None
        product_list =[]  
        product_ids = self.recipe_product_id.recipe_structure_ids
        print("print product ids ----------- ",product_ids)
        if product_ids:
            for prd in product_ids:
                product_dictt = (0, 0, {'parent_id': self.id ,
                                        'record_id': prd.product_id.id ,
                                     'product_id':prd.product_id.id, 
                                     'location_id': prd.location_id.id , 
                                     'qty_to_consum':prd.qty_to_consum})
    
                product_list.append(product_dictt)
        self.recipe_product_ids = product_list
        return
    
    
    def update_recipe_structure(self):
        exist = self.env['recipe.structure'].search([('parent_id', '=', self.recipe_product_id.id)])
        product_list = []
        for f in self.recipe_product_ids:
            if f.record_id == 0:
                product_dictt = {'recipe_structure_ids':[(0, 0, {'parent_id': self.recipe_product_id.id ,
                                    'product_id':f.product_id.id, 
                                    'location_id': f.location_id.id , 
                                    'qty_to_consum':f.qty_to_consum})]}
                product_list.append(product_dictt)
                rec = self.recipe_product_id.write(product_dictt)
            for ep in exist:
                if ep.product_id.id == f.product_id.id:
                    ep.parent_id = self.recipe_product_id.id
                    ep.product_id = f.product_id.id
                    ep.location_id = f.location_id.id
                    ep.qty_to_consum = f.qty_to_consum
        return 
    
    
    # @api.onchange('recipe_product_id')
    # def onchange_all_assets(self):
    #     self.recipe_product_ids = None
    #     product_list = []
    #     product_ids = self.recipe_product_id.recipe_structure_ids
    #     print("print product ids ----------- ",product_ids)
    #     if product_ids:
    #         for prd in product_ids:
    #             product_dictt = (0, 0, {'parent_id': prd.id ,
    #                      'product_id':prd.product_id.id, 
    #                      'location_id': prd.location_id.id , 
    #                      'qty_to_consum':prd.qty_to_consum})
    #             product_list.append(product_dictt)
    #         self.recipe_product_ids = product_list
    #     return
    
    
    
class RecipeProductLine(models.TransientModel):
    _name = 'recipe.product.wizard.line'
    _description = 'recipe.product.wizard.line'
    
    record_id = fields.Integer('Recipe Product Id')
    parent_id = fields.Many2one("recipe.product.wizard", string="Product")
    product_id = fields.Many2one("product.product", string="Product",domain="[('type','=','product')]", required=True)
    location_id = fields.Many2one("stock.location", string="Location",domain="[('usage','=','internal')]")
    qty_to_consum = fields.Float('Qty Consumed')

    
    
    
    