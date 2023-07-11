odoo.define('od_material_consumption.pos', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var rpc = require('web.rpc');
	var screens = require('point_of_sale.screens');

	var _t = core._t;
    var _super_product = models.PosModel.prototype;

	// Load Models here...

	models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes){
            var self = this;
            models.load_fields('product.product', ['is_recipe']);
            _super_product.initialize.apply(this, arguments);
        }
    });

	// End ProductListWidget start

	screens.ActionpadWidget.include({
		renderElement: function() {
			var self = this;
			this._super();
			this.$('.pay').click(function(){
				var order = self.pos.get_order();
				order.orderlines.models.forEach((line) => {
					if(line.product.is_recipe == true && line.product.product_tmpl_id){
					rpc.query({
						model: 'product.template',
						method: 'check_if_structure_available',
						args: [line.product.product_tmpl_id],
						kwargs: {'qty': line.quantity},
						}).then(function(output) {
							if (output.error == true){
								self.gui.show_screen('products');
								self.gui.show_popup('error',{
									'title': _t('Cant Add Product'),
									'body': _t(output.message)
								});
							}
					});
				}
				});
			});
		}
	});


	
});
