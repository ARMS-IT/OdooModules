odoo.define('altayibat_pos_receipt.receipt_address', function (require) {
	"use strict";

	var models = require("point_of_sale.models");
	var rpc = require('web.rpc');

	models.load_models({
    model:  'res.company',
    fields: ['id','partner_id','street','vat','street2','city','state_id'],
    loaded: function(self,companies){
        self.companies = companies;
        },
    });

//    models.load_models({
//    model:  'pos.config',
//    fields: ['branch_company_id'],
//    loaded: function(self,branch_company_id){
//        self.companies = companies;
//        },
//    });


    var _super_order = models.Order.prototype;

    var pos_models = models.PosModel.prototype.models;

    for(var i=0; i<pos_models.length; i++){
        var model= pos_models[i];
        if(model.model === 'res.company'){
             model.fields.push('street');
             model.fields.push('city');
             model.fields.push('state_id');
             model.fields.push('country_id');
             model.fields.push('logo');
        }
    }

    models.Order = models.Order.extend({
     	export_for_printing: function () {
            var self = this;

//            rpc.query({
//                    model: 'res.company',
//                    method: 'search_read',
//                    args: args,
//                });

            var orders = _super_order.export_for_printing.call(this);
            var order = this.pos.get_order();

            var company_partner;
            for (var i=0; i<posmodel.partners.length; i++){
            	if (posmodel.partners[i].id == this.pos.company.partner_id[0]){
            		company_partner = posmodel.partners[i]
            	}
            }
            if (company_partner!=undefined){
            	orders.company['street'] = company_partner.street;
            	orders.company['street2'] = company_partner.street2;
            	orders.company['city'] = company_partner.city;
                orders.company['country'] = company_partner.country_id[1];
            	orders.company['image'] = "data:image/png;base64," + this.pos.company.logo;
            }

            var branch_company;
            for (var i=0; i<this.pos.session.user_companies.allowed_branches.length; i++){
            	if (this.pos.session.user_companies.allowed_branches[i][0] == this.pos.config.branch_company_id[0]){
            		branch_company = this.pos.session.user_companies.allowed_branches[i][1]
            	}
            }
            if (branch_company!=undefined){
            	orders.company['bstreet'] = branch_company['street'];
            	orders.company['bstreet2'] = branch_company['street2'];
            	orders.company['bcity'] = branch_company['city'];
                orders.company['bcountry'] = branch_company['country'];
                orders.company['bvat'] = branch_company['vat'];
            }

            orders['shopname'] = this.pos.config.name;
            orders['shoplogo'] = "data:image/png;base64," + this.pos.config.image;

            // Res Functions for Convertion.
            function ConvertHexaDecimalToBase64(hexa_decimal_string) {
                return btoa(hexa_decimal_string.match(/\w{2}/g).map(function(res) {
                    return String.fromCharCode(parseInt(res, 16));
                }).join(""));
            }

            function ConvertDecimalToHexaDecimal(res) {
                var hexa_decimal = Number(res).toString(16);
                if (hexa_decimal.length < 2) {
                   hexa_decimal = "0" + hexa_decimal;
                }
                return hexa_decimal;
            };

            function ConvertAsciiToHexa(res){
                var result = [];
                res = btoa(unescape(encodeURIComponent((res))));
                res = atob(res);
                for (var n = 0, l = res.length; n < l; n ++){
                    var hex = Number(res.charCodeAt(n)).toString(16);
                    result.push(hex);
                }
                return result.join('');
            }


            // Get QR Code Data
            var seller = ConvertAsciiToHexa(this.pos.company.name);
            var seller_length = ConvertDecimalToHexaDecimal(seller.length/2);
            var QRSellerName = "01" + seller_length + seller;


            var seller_vat_length = ConvertDecimalToHexaDecimal(this.pos.company.vat.length);
            var QRSellerVat = "02" + seller_vat_length + ConvertAsciiToHexa(this.pos.company.vat);


            var order_date_length = ConvertDecimalToHexaDecimal(order.creation_date.toISOString().length);
            var order_date_string = String(order.creation_date.toISOString());
            var QROrderDate = "03" + order_date_length + ConvertAsciiToHexa(order_date_string);


            var order_total_with_tax = Math.round(order.get_total_with_tax() * 100) / 100;
            var order_total_with_tax_length = ConvertDecimalToHexaDecimal(String(order_total_with_tax).length);
            var QRTotalWithTax = "04" + order_total_with_tax_length + ConvertAsciiToHexa(String(order_total_with_tax));


            var order_tax_total = Math.round(order.get_total_tax() * 100) / 100;
            var order_tax_total_length = ConvertDecimalToHexaDecimal(String(order_tax_total).length);
            var QRTaxTotal = "05" + order_tax_total_length + ConvertAsciiToHexa(String(order_tax_total));


            var QRCodeHexaDecimal = QRSellerName+QRSellerVat+QROrderDate+QRTotalWithTax+QRTaxTotal
            var QRCodeBase64String = ConvertHexaDecimalToBase64(QRCodeHexaDecimal);

            orders.zatca_qr_code = QRCodeBase64String;
            return orders;
        },
    });

});
