odoo.define('bi_pos_order_types.PosCustomOrderType', function(require) {
	'use strict';
    var models = require('point_of_sale.models');
    	var core = require('web.core');
    	var _t = core._t;

    	models.load_models({
    		model: 'pos.order.type',
    		fields: ['name','id'],
    		domain: function(self) {
    			return [
    				['id', 'in', self.config.order_type_ids]
    			];
    		},
    		loaded: function(self, pos_custom_order_type) {

    			self.pos_custom_order_type = pos_custom_order_type;
    		},

    	});

      var _super_order = models.Order.prototype;
      models.Order = models.Order.extend({
        initialize: function(attr, options) {
            _super_order.initialize.call(this,attr,options);
            this.order_type_id = this.order_type_id || "";
            this.order_type = this.order_type || "";
        },

        set_order_type_id: function(order_type_id){
            this.order_type_id = order_type_id;
            this.trigger('change',this);

        },
        get_order_type_id: function(){
            return this.order_type_id;
        },
        set_order_type: function(order_type){
            this.order_type = order_type;
            this.trigger('change',this);

        },
        get_order_type: function(){
            return this.order_type;
        },

        export_as_JSON: function(){
            var json = _super_order.export_as_JSON.call(this);
            json.order_type_id = this.order_type_id;
            return json;
        },
        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments);
            this.order_type_id = json.order_type_id;
        },

    });
    });