from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_default_consumption_location(self):
        return self.env.ref('ts_recipe_mgt.stock_location_material_consumption').id

    is_recipe = fields.Boolean('Is Recipe')

    consumption_location_id = fields.Many2one(
        'stock.location', "Consumption Location", company_dependent=True, check_company=True, default=get_default_consumption_location,
        domain="[('usage', '=', 'inventory'), '|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
        help="This stock location will be used, instead of the default one, as the source location for stock moves generated when you do an inventory consumption.")

    recipe_structure_ids = fields.One2many('recipe.structure', 'parent_id', 'Recipe Structure')

    @api.onchange('is_recipe')
    def _onchange_set_p_service(self):
        if self.is_recipe:
            self.type = 'service'
        return

    def check_if_structure_available(self, *args, **kwargs):
        result = {'error': False, 'message': ''}
        if kwargs.get('qty'):
            qty = kwargs.get('qty')
            if qty:
                for product in self:
                    if self.is_recipe and self.recipe_structure_ids:
                        for rs in self.recipe_structure_ids:
                            requird_qty = float(qty) * rs.qty_to_consum
                            if rs.product_id and rs.product_id.qty_available >= requird_qty:
                                _logger.info(rs.product_id.qty_available)
                            else:
                                result['error'] = True
                                result['message'] = "{0} -> {1} has no required quantity for consumption. Required {2} but available {3}".format(product.name, rs.product_id.name, requird_qty, rs.product_id.qty_available)
                                return result
                        return result
                    else:
                        result['error'] = True
                        result['message'] = "No Recipe Structure available for product: {0}".format(product.name)
                    return result
                return result

class RecipeStructure(models.Model):
    _name = 'recipe.structure'
    _description = 'Recipe Structure'

    parent_id = fields.Many2one("product.template", string="Recipe Product", required=True)
    product_id = fields.Many2one("product.product", string="Product",domain="[('type','=','product')]")
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id')
    cost_price = fields.Float(related='product_id.standard_price')
    location_id = fields.Many2one("stock.location", string="Location",domain="[('usage','=','internal')]")
    company_id = fields.Many2one("res.company", string="Company")
    qty_to_consum = fields.Float('Qty Consumed')
