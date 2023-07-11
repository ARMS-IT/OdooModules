from odoo import models, fields, api, _


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    is_material_consumption = fields.Boolean('Material Consumption')
    material_consumption_name = fields.Char('Reference', default=_('New'))
    parent_product_id = fields.Many2one('product.template',string="Recipe Product")
    sale_order_id = fields.Many2one('sale.order',string="Order")
    pos_order_id = fields.Many2one('pos.order',string="Order")
    pos_session_id = fields.Many2one('pos.session', string="Session")

    @api.onchange('material_consumption_name')
    def onchange_material_consumption_name(self):
        if self.is_material_consumption:
            self.name = self.material_consumption_name

    @api.model
    def create(self, vals):
        if vals.get('material_consumption_name', _('New')) == _('New'):
            vals['material_consumption_name'] = self.env['ir.sequence'].next_by_code('material.consumption.request') or _('New')
        res = super(StockInventory, self).create(vals)
        if res.is_material_consumption:
            res.name = res.material_consumption_name
        return res

    def action_open_inventory_lines(self):
        self.ensure_one()
        if self.is_material_consumption:
            action = {
                'type': 'ir.actions.act_window',
                'views': [(self.env.ref('ts_recipe_mgt.stock_consumption_line_tree').id, 'tree')],
                'view_mode': 'tree',
                'name': _('Inventory Lines'),
                'res_model': 'stock.inventory.line',
            }
            context = {
                'default_is_editable': True,
                'default_inventory_id': self.id,
                'default_company_id': self.company_id.id,
            }
            # Define domains and context
            domain = [
                ('inventory_id', '=', self.id),
                ('location_id.usage', 'in', ['internal', 'transit'])
            ]
            if self.location_ids:
                context['default_location_id'] = self.location_ids[0].id
                if len(self.location_ids) == 1:
                    if not self.location_ids[0].child_ids:
                        context['readonly_location_id'] = True
            if self.product_ids:
                if len(self.product_ids) == 1:
                    context['default_product_id'] = self.product_ids[0].id
            action['context'] = context
            action['domain'] = domain
            return action
        else:
            return super(StockInventory, self).action_open_inventory_lines()


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    qty_to_consume = fields.Float('Qty to Consume')

#    def _get_virtual_location(self):
#        if self.inventory_id.is_material_consumption:
#            return self.product_id.with_context(force_company=self.company_id.id).consumption_location_id
#        return super(StockInventoryLine, self)._get_virtual_location()

    @api.onchange('qty_to_consume')
    def _compute_product_quantity(self):
        for rec in self:
            rec.product_qty = rec.theoretical_qty - rec.qty_to_consume

