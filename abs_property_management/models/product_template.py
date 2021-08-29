# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_property = fields.Boolean("Is Property")
    is_for_rent = fields.Boolean("For Rent")
    is_for_sale = fields.Boolean("For Sale")
    property_status = fields.Selection([('available_for_sale','Available for Sale'),('available_for_rent','Available for Rent'),('sold','Sold'),('booked','Booked')])

    property_price = fields.Float("Property Price")
    is_price_negotiable = fields.Boolean("Price Negotiable")
    property_type = fields.Selection([('residential', 'Residential'),('commercial', 'Commercial')])

    is_pg_accomodation = fields.Boolean("PG accomodation")
    is_pg_for_girls = fields.Boolean("PG for girls")
    is_pg_for_boys = fields.Boolean("PG for boys")
    is_pg_for_all = fields.Boolean("PG for all")
    is_tenant_students = fields.Boolean("Studentds")
    is_tenant_working = fields.Boolean("Working Professional")

    is_family = fields.Boolean("Family")
    is_single_man = fields.Boolean("Single Man")
    is_single_woman = fields.Boolean("Single Woman")

    property_for = fields.Selection([('sale', 'Sale'),('rent', 'Rent')], string="Property for")
    new_or_resale = fields.Selection([('new_booking','New Booking'),('resale','Resale')])
    residential_property = fields.Selection([('apartment','Apartment'),('plot','Plot'),('house_villa','House/Villa'),('farm_house','Farm House')])
    commercial_property = fields.Selection([('office','Office'),('shop','Shop'),('showroom','Showroom')])
    maintenance_charge = fields.Float("Maintenance Charge")
    maintenance_charge_type = fields.Selection([('one_time','- One Time'),('monthly','- Monthly'),('annually','- Annually')])
    deposit = fields.Float("Deposit")

    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    bedrooms = fields.Char("Bedrooms")
    bathrooms = fields.Integer("Bathrooms")
    balconies = fields.Integer("Balconies")
    furnishing = fields.Selection([('unfurnished','Unfurnished'),('semi-furnished','Semi-furnished'),('fully-furnished','Fully-furnished')])

    is_pooja_room = fields.Boolean("Pooja Room")
    is_study_room = fields.Boolean("Study Room")
    is_servant_room = fields.Boolean("Servant Room")
    is_other_room = fields.Boolean("Other Room")

    is_air_conditioned = fields.Boolean("Air Conditioned")
    is_piped_gas = fields.Boolean("Piped Gas")
    is_internet_wifi = fields.Boolean("Internet Wifi Connectivity")

    plot_facing = fields.Selection([('east','East'),('north_east','North East'),('north','North'),('north_west','North West'),('west','West'),('south_west','South West'),('south','South'),('south_east','South East')])
    allowed_construction_floors = fields.Integer("Allowed construction floors")
    facing_road_width = fields.Integer("Facing road width", help="Consider Area in Sq.Ft")
    is_corner_property = fields.Boolean("Corner Property")
    boundry_wall_mad = fields.Selection([('yes','Yes'),('no','No')])

    is_lifts = fields.Boolean("Lifts")
    is_maintenance_staff = fields.Boolean("Maintenance Staff")
    is_parks = fields.Boolean("Parks")
    is_visitor_parking = fields.Boolean("Visitors Parking")
    is_swimming_pool = fields.Boolean("Swimming Pool")
    is_fitness_center = fields.Boolean("Fitness Center/Gym")
    is_security = fields.Boolean("Security")

    washrooms = fields.Selection([('shared','Shared'),('none','None'),('one','1'),('two','2'),('three','3'),('more_than_three','3+')],default='none')
    is_waste_disposal = fields.Boolean("Waste Disposal")
    is_banquet_hall = fields.Boolean("Banquet Hall")
    is_powerback_up = fields.Boolean("Powerback up")
    is_food_court = fields.Boolean("Food Court" )
    is_conference_room = fields.Boolean("Conference room")
    is_security_alarm = fields.Boolean("Security Alarm")
    is_water_storage = fields.Boolean("Water Storage")
    is_bar_or_lounge = fields.Boolean("Bar/Lounge")
    is_shopping_center = fields.Boolean("Shopping Center")

    allowed_installments = fields.Many2many('property.installment', string = "Allowed Installments")

    built_up_area = fields.Integer("Built-Up Area", help="Consider Area in Sq.Ft")
    carpet_area = fields.Integer("Carpet Area", help="Consider Area in Sq.Ft")
    total_floors = fields.Integer("Total Floors")
    property_floors = fields.Integer("Property Floors")
    plot_area = fields.Integer("Plot area", help="Consider Area in Sq.Ft")

    is_propery_available = fields.Selection([('under_construction','Under Construction'),('ready_to_move','Ready to Move')])
    property_age = fields.Float("Property Age")
    property_available_form = fields.Date("Property available from")
    ownership = fields.Selection([('freehold','Freehold'),('leasehold','Leasehold'),('co_operative_society','Co-oprative society'),('poer_of_attorney','Power of Attorney')])
    partner_id = fields.Many2one('res.partner', string="Landlord")
    property_description = fields.Text("Property Description")

    is_parking = fields.Boolean("None")
    open_parking = fields.Integer("Open Parking")
    covered_parking = fields.Integer("Covered Parking")

    commission_ids = fields.One2many('company.commission','product_template_id', string="Commission Ids")
    tenancy_history_ids = fields.One2many('tenant.history','tenancy_id', string="Tenant History")

    contract_ids = fields.One2many('property.contract','tenancy_id', string="Contracts")
    total_contract = fields.Integer("Total Contracts", compute="compute_total_contracts")

    maintenance_ids = fields.One2many('property.maintenance','name', string="Maintenances")
    total_maintenance = fields.Integer("Total Maintenance", compute="compute_maintenance")

    total_installments = fields.Integer("Total Installments", compute="compute_installments")

    sale_order_id = fields.Many2one('sale.order',"Property Sale Order")

    current_property_user_id = fields.Many2one('res.users','Current Property User')
 
    def compute_installments(self):
        for record in self:
            count_installments = 0
            invoice_ids = self.env['account.move'].search([('invoice_origin','=',self.id)])
            if invoice_ids:
                for invoice_id in invoice_ids:
                    if invoice_id:
                        count_installments += 1
            record.total_installments = count_installments

    def compute_total_contracts(self):
        for record in self:
            count_contract = 0
            if record.contract_ids:
                for contract in record.contract_ids:
                    if contract:
                        count_contract += 1
            record.total_contract = count_contract

    def compute_maintenance(self):
        for record in self:
            count_maintenance = 0
            if record.maintenance_ids:
                for maintenance_id in record.maintenance_ids:
                    if maintenance_id:
                        count_maintenance += 1
            record.total_maintenance = count_maintenance

    @api.onchange('property_status')
    def onchange_property_status(self):
        for record in self:
            if record.property_status == 'available_for_rent':
                record.current_property_user_id = False
            if record.property_status == 'available_for_sale':
                record.current_property_user_id = False

    @api.onchange('property_type')
    def onchange_propert_type(self):
        for record in self:
            if record.property_type == 'residential':
                record.commercial_property = None
            elif record.property_type == 'commercial':
                record.residential_property = None

    @api.onchange('residential_property')
    def onchange_residential_property(self):
        for record in self:
            if record.residential_property == 'plot' and record.property_for == 'rent':
                raise ValidationError('Please select another propety for rent')

    @api.onchange('property_for')
    def onchange_property_for(self):
        for record in self:
            if record.property_for == 'rent' and record.residential_property == 'plot':
                raise ValidationError('Please select another propety for rent')
            if record.property_for == 'sale':
                record.property_status = 'available_for_sale'
            if record.property_for == 'rent':
                record.property_status = 'available_for_rent'

    def set_property_to_rent(self):
        for record in self:
            if record.property_status == 'booked':
                record.property_status = 'available_for_rent'

    def set_property_to_sale(self):
        for record in self:
            if record.property_status == 'sold':
                record.property_status = 'available_for_sale'
