# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields
from odoo.tools.translate import _
from odoo.exceptions import UserError,ValidationError
import logging
logger = logging.getLogger(__name__)
import requests
import base64
import json
from datetime import datetime


class ProductTemplate(models.Model):
	_inherit = "product.template"
	
	date_line_ids = fields.One2many("product.date.mapping", "product_tmp_id", string="Date Tracking", copy=True)

class ProductDateMapping(models.Model):
	_name = "product.date.mapping"

	effect_date = fields.Datetime(string="Effect Date",)
	expiry_date = fields.Datetime(string="Expiry Date",)
	status = fields.Boolean(string="Active")
	product_tmp_id = fields.Many2one("product.template", string="Dates", ondelete='cascade', index=True, copy=False)
	
	@api.constrains('effect_date', 'expiry_date')
	def _check_dates(self):
		for record in self:
			if record.expiry_date < fields.Datetime.now() or record.effect_date > record.expiry_date :
				raise ValidationError(_("Expiry date should be greater or equal to todays Date"))


class PosSession(models.Model):
	_inherit = "pos.session"
	
	sale_seq_no = fields.Char(string="SaleOrder No",compute="_compute_sequence")
	integration_flag = fields.Boolean(string="Success",tracking=True)	
	integration_log = fields.Text(string="Integration Log",tracking=True)	
	json_data = fields.Text(string="Json")	
		
	@api.depends('config_id', 'name')
	def _compute_sequence(self):
	
		today = fields.Datetime.now()
		year = str(today.year)
		year = year[2:]

		shop_name = self.config_id.name
		branch_seq = int(''.join(filter(str.isdigit, shop_name)))		
		branch = str(branch_seq)
		branch = branch[2:]

		name = str(self.name[4:])
		seq = year+''+branch+''+name
		logger.info(f"********* TokenData *****: {seq}.")
#		raise UserError(_('Item List ----%s') % (seq))
		self.sale_seq_no = year+''+branch+''+name
		
	def action_pos_session_closing_control(self):
		xxx = super(PosSession, self).action_pos_session_closing_control()
		self.send_pos_data()
		logger.info(f"********* SELLLLLF *****: {xxx}.")
    

	def send_pos_data(self):
		logger.info(f"********* API Integration started for alrashed POS ************.")
		try:
			logger.info(f"********* POS Alrashed Integration Started*******")
			items_list = []
			count = 0
			logger.info(f"********* Total Orders %s******* {len(self.order_ids)}")
			order_date = self.stop_at.strftime("%d/%m/%Y")
			company_id = "00101"
			salesperson = ""
			flag=False
			branch_id = int(''.join(filter(str.isdigit, self.config_id.name))) 	or ""	
				
			if self.config_id.company_id.identities_ids:
				company_id = self.config_id.company_id.identities_ids.id_number
			else:
				raise ValidationError(_("Please map Company ID in Company Form."))							
			

			if self.user_id.partner_id.identities_ids:
				saleperson = self.user_id.partner_id.identities_ids.id_number
			else:
				raise ValidationError(_("Please map the Salesperson ID."))							


			if not branch_id:
				raise ValidationError(_("BranchID is not mapped"))							

			for orders in self.order_ids.filtered(lambda t: t.state != 'paid'):
				count = count
				logger.info(f"********* Total Count %s******* {count}")
				for order_lines in orders.lines:
					items_data = {
						"Itemcode":order_lines.product_id.default_code or '',
						"Quantity": float(order_lines.qty) or "1.0",
						"UOM":str(order_lines.product_uom_id.name) or "1.0",
						"LineType": "S",
						"LastStatus": "520",
						"NextStatus": "560",
						"unitprice": float(order_lines.price_unit) or "0.0",
						"extendedprice": float(order_lines.price_subtotal) or "0.0",
					}
					items_list.append(items_data)
				count = count+1	

			names = set([k['Itemcode'] for k in items_list])
			dict1 = []
			for name in names:
				unit_price = []
				extendedprice = []
				qty = []
				uom = []
				for dict_ in items_list:
					if dict_['Itemcode'] == name:
						unit_price.append(dict_['unitprice'])
						extendedprice.append(dict_['extendedprice'])
						qty.append(dict_['Quantity'])
						uom.append(dict_['UOM'])

				dict1.append({'Itemcode': name, 'unitprice' : str(sum(unit_price)),'extendedprice' : str(sum(extendedprice)),'Quantity': str(sum(qty)),"LineType": "S","LastStatus": "520","NextStatus": "560","UOM": ' '.join(uom)})


			data = {
				"OrderHeader": {
					"Order_Company": company_id,
					"SalesOrderNo" : self.sale_seq_no or "",
					"Business_Unit": branch_id,
					"Doc_type": "QC",
					"Sold_to": str(salesperson),
					"order_date": order_date or '',
					"BaseCurrencyCode" : "SAR",
					"OrderDetail": items_list
				}
			}	
			
			logger.info(f"********* DATA *****: {data}.")
			post_url = "http://91.75.33.188:4928/Magicxpi4.13/MgWebRequester.dll?appname=IFSPOSIntegration&prgname=HTTP&arguments=-AHTTP_SalesOrder%23SalesOrder"
			post_result = requests.post(post_url, json=data)

			logger.info(f"********* POST Result *****: {post_result}.")
			post_result_json = post_result.json()
			if post_result_json['B4200310.F4211FSEndDoc']:
				for key,value in post_result_json['B4200310.F4211FSEndDoc'].items():
					if key == 'Success':
						flag = value or ''
					else:
						flag = False

			self.integration_log = post_result_json
			self.integration_flag = flag
			self.json_data = data
			
			logger.info(f"********* POST Result JSON *****: {post_result_json}.")
			#raise UserError(_('Item List ----%s') % (post_result_json))
		except Exception as e:
			raise e
			
