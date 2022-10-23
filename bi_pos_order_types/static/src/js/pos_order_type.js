odoo.define('bi_pos_order_types.PosOrderType', function(require) {
'use strict';

   const PosComponent = require('point_of_sale.PosComponent');
   const ProductScreen = require('point_of_sale.ProductScreen');
   const { useListener } = require('web.custom_hooks');
   const Registries = require('point_of_sale.Registries');


   class CustomOrderTypeButtons extends PosComponent {
	   constructor() {
		   super(...arguments);
		   useListener('click', this.onClick);
	   }
	   is_available() {
		   const order = this.env.pos.get_order();
		   return order
	   }
	   	async onClick() {
	   		var core = require('web.core');
	   		var _t = core._t;
	   		var order = this.env.pos.get_order();
			var orderlines = order.orderlines;
            if (orderlines.length === 0) {
                this.showPopup('ErrorPopup',{
                    'title': this.env._t('Empty Order'),
                    'body': this.env._t('There must be at least one product in your order before applying order type.'),
                });
                return;
            }
            else{
		   		let self = this;
				let lst = self.env.pos.pos_custom_order_type;
				let order = this.env.pos.get_order();

				const selectionList = this.env.pos.pos_custom_order_type.map(otype => ({
					id: otype.id,
					label: otype.name,
					isSelected:false,
					item: otype,
				}));

				const { confirmed, payload: selectedtype } = await this.showPopup(
					'SelectionPopup',
					{
						title: this.env._t('Select Types of POS order'),
						list: selectionList,
					}
				);

				if (confirmed) {
				order.set_order_type(selectedtype.name);
				order.set_order_type_id(selectedtype.id)
			}
			}
		}
   }
   CustomOrderTypeButtons.template = 'CustomOrderTypeButtons';
   ProductScreen.addControlButton({
	   component: CustomOrderTypeButtons,
	   condition: function() {
		   return this.env.pos.config.enable_order_type;
	   },
   });
   Registries.Component.add(CustomOrderTypeButtons);
   return CustomOrderTypeButtons;
});
