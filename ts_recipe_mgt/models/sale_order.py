from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    sales_conpt_count = fields.Integer('Consumption',compute="_sales_consumption_count")

    def _sales_consumption_count(self):
        for record in self:
            inv_id = self.env['stock.inventory'].search([('sale_order_id', '=', record.id),('is_material_consumption', '=',True)])
            record.sales_conpt_count = len(inv_id)
        return

    def sales_consumption_list(self):
        return {
                'name':"Consumption",
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(self.env.ref('stock.view_inventory_tree').id, 'tree'),
                          (self.env.ref('ts_recipe_mgt.view_consumption_request_form').id, 'form')],
                'res_model': 'stock.inventory',
                'type': 'ir.actions.act_window',
                'target': 'Current',
                'domain': "[('id', 'in', %s)]" % self.env['stock.inventory'].search([('sale_order_id', '=', self.id),('is_material_consumption', '=',True)]).ids,

            }




    def action_confirm(self):
        product_list = [];location_list = []
        res = super(SaleOrder, self).action_confirm()
        sale_lines = self.order_line
        for f in sale_lines:
            if f.product_id.product_tmpl_id.is_recipe:
                for t in f.product_id.product_tmpl_id.recipe_structure_ids:
                    product_list.append(t.product_id.id)
                    location_list.append(t.location_id.id)
                stock_inventory_id = self.env['stock.inventory'].create({'location_ids':location_list,'product_ids':  product_list,'accounting_date':self.date_order,'is_material_consumption':True,'sale_order_id':self.id})
                result = stock_inventory_id.action_start()
                stk_inv = stock_inventory_id.action_open_inventory_lines()
                stock_invty_line_id = self.env['stock.inventory.line'].search([('inventory_id','=',stock_inventory_id.id)])
                for inv in stock_invty_line_id:
                    for recipe in  f.product_id.product_tmpl_id.recipe_structure_ids:
                        if recipe.product_id.id == inv.product_id.id:
                            inv.qty_to_consume = recipe.qty_to_consum * f.product_uom_qty
                    inv._compute_product_quantity()
                stk_inv = stock_inventory_id.action_validate()
        return res