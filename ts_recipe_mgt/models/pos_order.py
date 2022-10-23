from odoo import models, fields, api, _
#from mock.mock import self
from odoo.exceptions import AccessError, UserError, ValidationError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    pos_conpt_count = fields.Integer('Consumption', compute="_pos_consumption_count")

    def _pos_consumption_count(self):
        for record in self:
            inv_id = self.env['stock.inventory'].search(
                [('pos_order_id', '=', record.id), ('is_material_consumption', '=', True)])
            record.pos_conpt_count = len(inv_id)
        return

    def pos_consumption_list(self):
        return {
            'name': "Consumption",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('stock.view_inventory_tree').id, 'tree'),
                      (self.env.ref('ts_recipe_mgt.view_consumption_request_form').id, 'form')],
            'res_model': 'stock.inventory',
            'type': 'ir.actions.act_window',
            'target': 'Current',
            'domain': "[('id', 'in', %s)]" % self.env['stock.inventory'].search(
                [('pos_order_id', '=', self.id), ('is_material_consumption', '=', True)]).ids,

        }


    def create(self, vals):

        product_list = [];location_list = []
        res = super(PosOrder, self).create(vals)
        pos_lines = res.lines
        for f in pos_lines:
            if f.product_id.product_tmpl_id.is_recipe:
                parent_product = f.product_id.product_tmpl_id
                print("Parent Product is ++++++++++ ",parent_product)
                for t in f.product_id.product_tmpl_id.recipe_structure_ids:
                    product_list.append(t.product_id.id)
                    location_list.append(t.location_id.id)
                stock_inventory_id = self.env['stock.inventory'].create({'location_ids':location_list,'product_ids':  product_list,'parent_product_id': parent_product.id,'accounting_date':res.date_order,'is_material_consumption':True,'pos_order_id':res.id,'pos_session_id':res.session_id.id})
                result = stock_inventory_id.action_start()
                stk_inv = stock_inventory_id.action_open_inventory_lines()
                stock_invty_line_id = self.env['stock.inventory.line'].search([('inventory_id','=',stock_inventory_id.id)])
                for inv in stock_invty_line_id:
                    for recipe in f.product_id.product_tmpl_id.recipe_structure_ids:
                        if recipe.product_id.id == inv.product_id.id:
                            print("this is the product qty",f)
                            print("this is the product name",recipe.product_id.name)
                            inv.qty_to_consume = recipe.qty_to_consum * f.qty
                    inv._compute_product_quantity()
                stk_inv = stock_inventory_id.action_validate()
        return res

class PosSession(models.Model):
    _inherit = 'pos.session'

    pos_session_conpt_count = fields.Integer('Consumption', compute="_pos_session_consumption_count")

    def _pos_session_consumption_count(self):
        for record in self:
            inv_id = self.env['stock.inventory'].search(
                [('pos_session_id', '=', record.id), ('is_material_consumption', '=', True)])
            record.pos_session_conpt_count = len(inv_id)
        return

    def pos_session_consumption_list(self):
        return {
            'name': "Consumption",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('stock.view_inventory_tree').id, 'tree'),
                      (self.env.ref('ts_recipe_mgt.view_consumption_request_form').id, 'form')],
            'res_model': 'stock.inventory',
            'type': 'ir.actions.act_window',
            'target': 'Current',
            'domain': "[('id', 'in', %s)]" % self.env['stock.inventory'].search(
                [('pos_session_id', '=', self.id), ('is_material_consumption', '=', True)]).ids,

        }
        
    def action_pos_session_closing_control(self):
        res = super(PosSession, self).action_pos_session_closing_control()
        move_lines = self.env['stock.move.line'].search([('pos_session_id','=',self.id)])
        pos_orders = self.env['pos.order'].search([('session_id','=',self.id)])
        for mv in move_lines:
            mv.compute_unitcost_product()
        for order in pos_orders:
            if order.session_id.picking_ids:
                for pick in order.session_id.picking_ids:
                    picking_lines = pick.move_line_ids_without_package
                for pl in picking_lines:
                        pl.compute_unitcost_product()
        return res
        
        
