from odoo import api, fields, models, _


class PosOrderType(models.Model):
	_name = 'pos.order.type'
	_description = "POS Order Types"

	name = fields.Char('Name', required=True)


class PosConfig(models.Model):
	_inherit = 'pos.config'

	enable_order_type = fields.Boolean('Enable Type of POS order')
	order_type_ids = fields.Many2many('pos.order.type', string='Type of POS order')


class pos_order(models.Model):
	_inherit = 'pos.order'

	order_type_id = fields.Many2one('pos.order.type',string='Type of POS order ')

	def _order_fields(self, ui_order):
		res = super(pos_order, self)._order_fields(ui_order)
		res.update({
			'order_type_id': ui_order.get('order_type_id'),
			})
		return res
