# -*- coding: utf-8 -*-

import json
import pytz
import hashlib
import base64
import qrcode, math
from datetime import datetime
from io import BytesIO
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.http import request
from odoo.addons.ehcs_qr_code_base.models.qr_code_base import generate_qr_code
import uuid
from odoo.exceptions import ValidationError
import codecs
from .fatoorah import Fatoora
from .xml_generator import generate_einvoice_xml

VAT_CHECKBOX_FIELDS = [
    'third_party_invoice',
    'short_invoice', 
    'virtual_import', 
    'export_invoice'
]

SIMPLE_CHECKBOX_FIELDS = [
    'third_party_invoice', 
    'short_invoice', 
    'virtual_import',
]

CREDIT_DEBIT_CHECKBOX_FIELDS = [
    'third_party_invoice', 
    'export_invoice',
    'short_invoice',
]

FIELD_LABEL = {
    'debit_credit_note':'Debit/Credit Note',
    # 'on_vendor_behalf':'On Behalf the vendor',
    'third_party_invoice':'Third party generated Invoice',
    'virtual_import':'Virtual Import',
    'export_invoice':'Export Invoice',
    'short_invoice':'Short Invoice'
}


class SequenceMixin(models.AbstractModel):
    """Mechanism used to have an editable sequence number.

    Be careful of how you use this regarding the prefixes. More info in the
    docstring of _get_last_sequence.
    """

    _inherit = 'sequence.mixin'
    
    def _set_next_sequence(self):
        """Set the next sequence.

        This method ensures that the field is set both in the ORM and in the database.
        This is necessary because we use a database query to get the previous sequence,
        and we need that query to always be executed on the latest data.

        :param field_name: the field that contains the sequence.
        """
        self.ensure_one()
        last_sequence = self._get_last_sequence()
        new = not last_sequence
        if new:
            last_sequence = self._get_last_sequence(relaxed=True) or self._get_starting_sequence()

        format, format_values = self._get_sequence_format_param(last_sequence)

        if self._name == 'account.move':
            if self.move_type == 'out_invoice':
                if self.invoice_type == 'vat':
                    format_values['prefix1'] = 'EINV'
                elif self.invoice_type == 'simple':
                    format_values['prefix1'] = 'SINV'

            elif self.move_type == 'out_refund':
                format_values['prefix1'] = 'CRN'

            elif self.move_type == 'in_refund':
                format_values['prefix1'] = 'DRN'

        if new:
            format_values['seq'] = 0
            format_values['year'] = self[self._sequence_date_field].year % (10 ** format_values['year_length'])
            format_values['month'] = self[self._sequence_date_field].month
        format_values['seq'] = format_values['seq'] + 1
        self[self._sequence_field] = format.format(**format_values)
        self._compute_split_sequence()

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('invoice_line_ids.discount', 'invoice_line_ids.discount_amount')
    def _compute_total_discount(self):
        for move in self:
            total_discount_percent = 0.0
            total_discount_amount = 0.0
            total_discounts = 0.0
            for line in move.invoice_line_ids:
                total_discounts += line.discount
                total_discount_amount += line.discount_amount

            if total_discounts > 0:
                total_discount_percent = total_discounts / len(move.invoice_line_ids)

            move.total_discount_percent = total_discount_percent
            move.total_discount = total_discount_amount

    def action_generate_report(self):
        return self.env.ref('zatca_e_invoicing.zatca_account_invoices').report_action(self)

    def convert_datetime_to_timestamp(self):
        """
        """
        invoice_timestamp = 0
        if self.invoice_time:
            invoice_timestamp = datetime.timestamp(self.invoice_time)
        return invoice_timestamp

    def get_qr_string(move):
        try:
            fatoorah_obj =  Fatoora(seller_name=move.qr_seller_name,tax_number=move.qr_seller_vat, invoice_date=move.qr_invoice_time, total_amount=move.qr_amount_total, tax_amount=move.qr_tax_total)
            qr_string = fatoorah_obj.base64
            move.qr_string = qr_string
            move.qr_fail_reason = str()
            # qr_string = codecs.encode(codecs.decode(hex_string, 'hex'), 'base64').decode()
            return qr_string
        except Exception as e:
            move.qr_fail_reason = e
            return e

    @api.depends('invoice_date', 'invoice_time', 'amount_by_group', 'company_id', 'amount_total', 'vendor_id', 'vendor_vat')
    def _compute_qr_vals(self):
        for move in self:
            if self.special_billing_agreement == 'third_party':
                qr_seller_name = move.vendor_id.name
                qr_seller_vat = move.vendor_vat or ''
            else:
                qr_seller_name = move.company_id.name
                qr_seller_vat = move.company_id.vat or ''
            
            qr_invoice_time = move.convert_datetime_to_timestamp()
            qr_amount_total = move.amount_total
            qr_tax_total = move.amount_tax
            
            # assign values
            move.qr_seller_name = qr_seller_name
            move.qr_seller_vat = qr_seller_vat
            move.qr_invoice_time = qr_invoice_time
            move.qr_amount_total = qr_amount_total
            move.qr_tax_total = qr_tax_total
            move.get_qr_string()
            base_domain = self.env['ir.config_parameter'].sudo().get_param('web.base.domain')
            move.qr_image = self.generate_qr("{}{}".format(base_domain,move.get_portal_url()))
            data = {
                'Seller Name':qr_seller_name,
                'Seller VAT':qr_seller_vat,
                'Issue Date':qr_invoice_time,
                'Total Amount (Tax Incl.)':qr_amount_total,
                'Vat Amount':qr_tax_total,
            }
            move.qr_image_zatca = self.generate_qr(move.qr_string)

    def generate_qr(self, data):
        qr_code = str()
        qr = qrcode.QRCode(
            version=5,
            box_size=5,
            border=2
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black',back_color='white')
        output_buffer = BytesIO()
        img.save(output_buffer, format='png')
        byte_data = output_buffer.getvalue()
        base64_str = base64.b64encode(byte_data)
        return base64_str

    invoice_type = fields.Selection([
        ('vat', 'E-Vat Invoice'),
        ('simple', 'Simplified E-Invoice'),
        # ('debit', 'Debit Note'),
        # ('credit', 'Credit Note'),
        ], default="vat", required=False)

    # move_type = fields.Selection(selection=[
    #         ('entry', 'Journal Entry'),
    #         ('out_invoice', 'Customer Invoice'),
    #         ('out_refund', 'Customer Credit Note'),
    #         ('in_invoice', 'Vendor Bill'),
    #         ('in_refund', 'Vendor Credit Note'),
    #         ('out_receipt', 'Sales Receipt'),
    #         ('in_receipt', 'Purchase Receipt'),
   
    debit_credit_note = fields.Boolean(string="Debit/Credit Note", default=False)
    on_vendor_behalf = fields.Boolean(string="On Behalf the vendor", default=False)
    third_party_invoice = fields.Boolean(string="Third party generated invoice", default=False)
    virtual_import = fields.Boolean(string="Virtual Import", default=False)
    export_invoice = fields.Boolean(string="Export Invoice", default=False)
    short_invoice = fields.Boolean(string="Short Invoice", default=False)

    # Invoice Number (using Default)    
    uuid_number = fields.Char(string='UUID')
    invoice_hash_number = fields.Char(string='Reference Hash Invoice Number', readonly=True)

    def get_previous_invoice_hash_number(self):
        all_moves = [move for move in self.env['account.move'].sudo().search([]).sorted(lambda move:move.id)]
        for move in self:
            previous_invoice_hash_number = str()

            if all_moves.index(move) == 0:
                previous_invoice_hash_number = 'NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ=='
            
            if all_moves.index(move) > 0:
                previous_move = all_moves[all_moves.index(move) - 1]
                previous_invoice_hash_number = previous_move.invoice_hash_number
            
            move.update({'previous_invoice_hash_number':previous_invoice_hash_number})

    previous_invoice_hash_number = fields.Char(string='Previous Hash Invoice Number', compute="get_previous_invoice_hash_number", readonly=True)

    # QR-Code related fields
    qr_image = fields.Binary("QR Code", copy=False, compute='_compute_qr_vals', store=False)
    qr_image_zatca = fields.Binary("Zatca QR Code", copy=False, compute='_compute_qr_vals', store=False)

    qr_seller_name = fields.Char("Seller's Name", compute="_compute_qr_vals")
    qr_seller_vat = fields.Char("Seller's Vat", compute="_compute_qr_vals")
    qr_invoice_time = fields.Char("Invoice Timestamp (Date and Time)", compute="_compute_qr_vals")
    qr_amount_total = fields.Char("Electronic Invoice Total (With VAT)", compute="_compute_qr_vals")
    qr_tax_total = fields.Char("VAT Total", compute="_compute_qr_vals")
    qr_fail_reason = fields.Text("QR Failure Reason", compute="_compute_qr_vals")
    qr_string = fields.Char(compute="_compute_qr_vals", string="QR Base64 String")

    is_acknowledged = fields.Boolean("Acknowledged")

    business_process_type = fields.Text("Business Process Type", required=True, default="reporting:1.0")


    def _compute_xml_json_str(self):
        """
        """
        for move in self:
            res = dict()
            res["ProfileID"] = move.business_process_type
            res["ID"] = move.id
            res["IssueDate"] = move.uuid_number
            res["IssueDate"] = move.invoice_time.date().strftime("%Y-%M-%d")
            res["IssueTime"] = move.invoice_time.time().strftime("%H:%M:%S")
            res["InvoiceTypeCode"] = move.invoice_type_code
            res["DocumentCurrencyCode"] = move.currency_id.name
            res["TaxCurrencyCode"] = move.currency_id.name
            res["AdditionalDocumentReference"] = [
                {
                    "ID": "ICV", 
                    "UUID": move.id,
                },
                {
                    "ID": "PIH", 
                    "Attachment": {
                        "EmbeddedDocumentBinaryObject": move.previous_invoice_hash_number,
                    }
                },
                {
                    "ID": "QR",
                    "Attachment": {
                        "EmbeddedDocumentBinaryObject": move.qr_string,
                    }
                }
            ]

            res["AccountingSupplierParty"] = [
                {
                    "Party": {
                        "PostalAddress": {
                            "StreetName": (move.partner_id.street + move.partner_id.street2) if move.partner_id.street2 else move.partner_id.street,
                            "BuildingNumber": move.partner_id.building_number,
                            "CityName": move.partner_id.city,
                            "CountrySubentity": move.partner_id.country_id.name,
                            "Country": {
                                "IdentificationCode": move.partner_id.country_id.code
                            }
                        },
                        "PartyTaxScheme": {
                            "CompanyID": move.partner_id.company_id.vat,
                            "TaxScheme": {
                                "ID": "VAT"
                            }
                        },
                        "PartyLegalEntity": {
                            "RegistrationName": move.partner_id.name,
                        }
                    }
                },
            ]

            vendor = move.company_id.partner_id
            if move.special_billing_agreement == 'third_party':
                vendor = move.vendor_id

            res["AccountingCustomerParty"] = [
                {
                    "Party": {
                        "PostalAddress": {
                            "StreetName": (vendor.street + vendor.street2) if vendor.street2 else vendor.street,
                            "BuildingNumber": vendor.building_number,
                            "PlotIdentification": vendor.additional_number,
                            "CitySubdivisionName": vendor.district,
                            "CityName": vendor.city,
                            "PostalZone": vendor.zip,
                            "CountrySubentity": vendor.country_id.name,
                            "Country": {
                                "IdentificationCode": vendor.country_id.code,
                            }
                        },
                        "PartyTaxScheme": {
                            "CompanyID": move.company_id.vat,
                            "TaxScheme": {
                                "ID": "VAT"
                            }
                        },
                        "PartyLegalEntity": {
                            "RegistrationName": vendor.name,
                        }
                    }
                },
            ]

            res["Delivery"] = {
                "ActualDeliveryDate": move.supply_date.strftime("%Y-%m-%d"), 
                "LatestDeliveryDate": move.supply_end_date.strftime("%Y-%m-%d"),
            }
            res["PaymentMeans"] = {
                "PaymentMeansCode": move.payment_mean_id.name
            }
            res["TaxTotal"] = [
                {
                    "TaxAmount": move.amount_tax,
                    "TaxSubtotal": {
                        "TaxableAmount": move.amount_untaxed,#--Subtotal
                        "TaxSubtotalTaxAmount": move.amount_tax,
                        "TaxCategory": { #tODISCUSS
                            "ID": "S",
                            "Percent": 15,
                            "TaxScheme": {
                                "ID": "VAT"
                            }
                        }
                    }
                },
                {
                    "TaxAmount": move.amount_tax,
                },
            ]
            res["LegalMonetaryTotal"] = {
                "LineExtensionAmount": move.amount_untaxed,
                "TaxExclusiveAmount": move.amount_untaxed,
                "TaxInclusiveAmount": move.amount_total,
                "AllowanceTotalAmount": 0,
                "PayableAmount": move.amount_total,
            }
            invoice_lines = list()
            for line in move.invoice_line_ids:
                invoice_lines.append({
                    "ID": line.id,
                    "InvoicedQuantity": line.quantity,
                    "LineExtensionAmount": line.price_subtotal,
                    "TaxTotal": {
                        "TaxAmount": line.tax_amount,
                        "RoundingAmount": line.price_total,
                    },
                    "Item": {
                        "Name": line.product_id.name,
                        "ClassifiedTaxCategory": [{
                            "ID": "S",
                            "Percent": tax_info.amount,
                            "TaxScheme": {
                                "ID": "VAT"
                            }
                        } for tax_info in line.tax_ids]
                    },
                    "Price": {
                        "PriceAmount": line.price_total
                    }
                })
            res["InvoiceLine"] = invoice_lines
            xml_json_str = json.dumps(res, indent=4)
            clean_xml_data = generate_einvoice_xml(res)
            
            move.update({
                    'xml_json_str':xml_json_str,
                    'invoice_xml_document':base64.b64encode(clean_xml_data.encode('utf-8')),
                    'invoice_xml_document_filename': "E-Invoice{}.xml".format(move.id)
                })

    xml_json_str = fields.Text("JSON For XML", compute="_compute_xml_json_str")
    invoice_xml_document = fields.Binary("Invoice XML Document", compute="_compute_xml_json_str")
    invoice_xml_document_filename = fields.Char("Invoice XML Document Filename", compute="_compute_xml_json_str")
    

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        """
        res = super(AccountMove, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        return res

    def action_acknowledged(self):
        for move in self:
            move.update({'is_acknowledged':True})

    # @api.depends('invoice_type')
    # def _compute_invoice_type_code(self):
    #     for inv in self:
    #         inv.invoice_type_code = '100'
            
    #         if inv.invoice_type in ['vat', 'simple']:
    #             inv.invoice_type_code = '100'

    #         elif inv.invoice_type in ['credit', 'debit']:
    #             inv.invoice_type = '200'

    @api.depends("invoice_type", "third_party_invoice", "transaction_type", "special_billing_agreement")
    def _compute_invoice_tx_code(self):
        for inv in self:
            invoice_tx_code = str()
            if inv.invoice_type == 'vat':
                invoice_tx_code += "01"
            elif inv.invoice_type == 'simple':
                invoice_tx_code += "02"
            else:
                invoice_tx_code += "00"

            if inv.third_party_invoice:
                invoice_tx_code += "1"
            else:
                invoice_tx_code += "0"

            if inv.transaction_type == 'nominal':
                invoice_tx_code += "1"
            else:
                invoice_tx_code += "0"

            if inv.transaction_type == 'export':
                invoice_tx_code += "1"
            else:
                invoice_tx_code += "0"
            
            if inv.transaction_type == 'summary':
                invoice_tx_code += "1"
            else:
                invoice_tx_code += "0"

            if inv.special_billing_agreement == 'self':
                invoice_tx_code += "1"
            else:
                invoice_tx_code += "0"

            inv.invoice_tx_code = invoice_tx_code

    @api.depends('move_type','invoice_type')
    def _compute_inv_type_code(self):
        for invoice in self:
            invoice.invoice_type_code = ''
            if invoice.move_type == 'out_invoice':
                invoice.invoice_type_code = '388'
            elif invoice.move_type == 'out_refund':
                invoice.invoice_type_code = '381'

            elif invoice.move_type == 'in_refund':
                invoice.invoice_type_code = '383'



    invoice_type_code = fields.Selection([
        ("380", '380 Commercial invoice'),
        ("381", '381 Credit note'),
        ("382", '382 Commission note'),
        ("383", '383 Debit note'),
        ("384", '384 Corrected invoice'),
        ("385", '385 Consolidated invoice'),
        ("386", '386 Prepayment invoice'),
        ("387", '387 Hire invoice'),
        ("388", '388 Tax invoice'),
        ("389", '389 Self-billed invoice'),
        ("390", '390 Delcredere invoice'),
        ("394", '394 Lease invoice'),
        ("395", '395 Consignment invoice')], string="Invoice Type Code", compute="_compute_inv_type_code")
    invoice_tx_code = fields.Char(string="Invoice Transaction Code", compute="_compute_invoice_tx_code")

    contract_ref = fields.Char("Contract ID")

    @api.model
    def _get_default_time(self):
        """
        """
        tz = pytz.timezone(self.env.user.tz or "UTC")
        current_time = fields.Datetime.now()
        current_time = pytz.utc.localize(current_time).astimezone(tz)
        t, hours = divmod(current_time.hour, 24)
        t, minutes = divmod(current_time.minute, 60)
        minutes = minutes/60.0
        return hours + minutes

    @api.depends('invoice_time')
    def _compute_invoice_date(self):
        for move in self:
            move.invoice_date = False
            if move.invoice_time:
                move.invoice_date = move.invoice_time.date()

    def _compute_invoice_datetime(self):
        for move in self:
            move.invoice_time = fields.Datetime.now()

    # Invoice Date (using Default)
    invoice_time = fields.Datetime("Invoice Time", readonly=False, required=False)
    invoice_date = fields.Date(compute="_compute_invoice_date")

    supply_date = fields.Date("Supply Date")
    supply_end_date = fields.Date("Supply End Date")


    @api.depends('company_id', 'vendor_id', 'special_billing_agreement')
    def _compute_vendor_vat(self):
        for move in self:
            if move.special_billing_agreement == 'third_party':
                move.vendor_vat_group_reg = move.vendor_id.group_vat_reg
            else:
                move.vendor_vat_group_reg = move.company_id.group_vat_reg

    def _get_report_base_filename(self):
        """
        Get Report Modified Name based on
        - Vat
        - Issue Date
        - Issue Time
        - IRN
        """
        filename = str()
        if self.customer_vat:
            filename += "{}_".format(self.customer_vat)
       
        if self.invoice_time:
            filename += datetime.strftime(self.invoice_time, "%d-%m-%Y_%H:%M")

        filename += "{}_".format(self.name)
        return filename

    import_invoice_date = fields.Date(string='Import Invoice Date')
    vendor_id = fields.Many2one('res.partner', "Vendor")
    vendor_vat = fields.Char("Vendor VAT", related="vendor_id.vat")
    vendor_vat_group_reg = fields.Char("Group VAT Registration Number", compute="_compute_vendor_vat")
    commercial_reg = fields.Char("Commercial Registration Number")
    vendor_reg_id = fields.Char("Vendor Registration ID")
    vendor_ip = fields.Char("Vendor IP")

    # Customer Name (default Partner_id)
    # Customer Addres (using default)
    customer_vat = fields.Char(related="partner_id.vat", string="Customer VAT Number")
    customer_confirmation_msg = fields.Text("Customer Confirmation Message for VAT Calculation.")
    debit_credit_note_reason = fields.Text(string="Debit/Credit Note Reason", ondelete=False)

    po_number = fields.Char(string='Purchase Number')
    
    # TODO
    total_discount_percent = fields.Float("Total Discount %", compute="_compute_total_discount")
    total_discount = fields.Monetary("Total Discount", compute="_compute_total_discount")

    inv_payment_type = fields.Selection([
            ('b2b-b2g', 'B2B or B2G (Cash, Credit Note)'),
            ('b2c', 'B2C (Cash, Bank Transfer, Credit Card)'),
        ])
    payment_condition = fields.Text("Payment Conditions")

    special_billing_agreement = fields.Selection([
            ('self','Self-Billed Invoice'), 
            ('third_party', 'Third Party Billed Invoice on Behalf of supplier.')
        ], default='self')

    transaction_type = fields.Selection([
            ('nominal', 'Nominal Supply'), 
            ('export', 'Export'), 
            ('summary','Summary')
        ], default='nominal')

    vat_exempt_reason = fields.Text("VAT Exemption Reason")


    @api.depends("total_discount")
    def _compute_discount_allowance(self):
        for inv in self:
            inv.discount_allowance = False
            if inv.total_discount > 0:
                inv.discount_allowance = True

    payment_mean_id = fields.Many2one('account.payment.mean', string="Payment Mean")
    discount_allowance = fields.Boolean("Allowance (Discount)", compute="_compute_discount_allowance")

    @api.constrains('special_billing_agreement')
    def check_special_billing_agreement(self):
        if self.special_billing_agreement == 'third_party' and self.move_type == 'out_invoice':
            if not self.vendor_vat or not self.customer_vat:
                raise ValidationError(_("Vendor VAT or Customer VAT not found."))
        else:
            if not self.company_id.vat:
                raise ValidationError(_("Company VAT not found."))

    def get_hash(self, uuid):
        """
        """
        hash_object = hashlib.md5(str(uuid).encode())
        md5_hash = hash_object.hexdigest()
        return md5_hash

    @api.model
    def create(self, vals):
        """
        """
        vals['uuid_number'] = uuid.uuid4()
        vals['invoice_hash_number'] = self.get_hash(vals.get('uuid_number'))
        vals['invoice_time'] = datetime.now()
        res = super(AccountMove, self).create(vals)
        return res

    @api.onchange('invoice_type')
    def onchange_invoice_type(self):
        """
        Reset the checkbox fields
        """
        self.debit_credit_note = False
        self.on_vendor_behalf = False
        self.third_party_invoice = False
        self.virtual_import = False
        self.export_invoice = False
        self.short_invoice = False
        if self.invoice_type == 'simple':
            self.special_billing_agreement = False
            self.inv_payment_type = 'b2c'
            self.payment_mean_id = self.env.ref("zatca_e_invoicing.payment_mean_30").id
        if self.invoice_type == 'vat':
            self.inv_payment_type = 'b2b-b2g'
            self.payment_mean_id = self.env.ref("zatca_e_invoicing.payment_mean_30").id

    # @api.constrains('third_party_invoice', 'debit_credit_note', 'on_vendor_behalf', 'short_invoice', 'virtual_import', 'export_invoice')
    # def check_bool_data(self):
    #     """
    #     """
    #     for move in self:
    #         CHECKABLE_FIELDS = list()
    #         if move.invoice_type == 'vat':
    #             CHECKABLE_FIELDS = VAT_CHECKBOX_FIELDS

    #         elif move.invoice_type == 'simple':
    #             CHECKABLE_FIELDS = SIMPLE_CHECKBOX_FIELDS

    #         elif move.invoice_type in ['debit', 'credit']:
    #             CHECKABLE_FIELDS = CREDIT_DEBIT_CHECKBOX_FIELDS

    #         for field in CHECKABLE_FIELDS:
    #             if not getattr(move, field) and move.move_type == 'out_invoice':
    #                 raise ValidationError(_("Please check {} Checkbox ".format(FIELD_LABEL[field])))

class PaymentMean(models.Model):
    _name = 'account.payment.mean'

    name = fields.Char("Payment Mean", required=True)
    code = fields.Char("Payment Mean Code", required=True)
    description = fields.Text("Description")

    def name_get(self):
        name_list = []
        for record in self:
            name = "[{}] {}".format(record.code, record.name)
            name_list += [(record.id, name)]
        return name_list


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    peppol_code = fields.Char("PEPPOL Code")

class Product(models.Model):
    _inherit = 'product.product'

    peppol_code = fields.Char("PEPPOL Code")

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('tax_ids', 'product_id', 'discount', 'quantity')
    def _compute_tax_amount(self):
        for line in self:
            tax_amount = 0.0
            if line.tax_ids:
                line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
                subtotal = line.quantity * line_discount_price_unit
                taxes = line.tax_ids
                force_sign = -1 if line.move_id.move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
                taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(line_discount_price_unit, quantity=line.quantity, currency=line.currency_id, product=line.product_id, partner=line.partner_id, is_refund=line.move_id.move_type in ('out_refund', 'in_refund'))
                tax_amount = taxes_res.get('total_included') - taxes_res.get('total_excluded')
            line.tax_amount = tax_amount

    @api.depends("discount", "price_unit", "quantity", "price_subtotal")
    def _compute_discount_amount(self):
        for line in self:
            discount_amount = 0.0
            if line.discount:
                line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
                discount_amount = (line.quantity * line.price_unit) - (line.quantity * line_discount_price_unit)
            line.discount_amount = discount_amount

    discount_amount = fields.Monetary(compute="_compute_discount_amount")
    tax_amount = fields.Monetary(compute="_compute_tax_amount")
    peppol_code = fields.Char("PEPPOL Code", related="product_id.peppol_code")
    move_type = fields.Selection(selection=[
            ('entry', 'Journal Entry'),
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note'),
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
            ('out_receipt', 'Sales Receipt'),
            ('in_receipt', 'Purchase Receipt'),
        ], string='Type', required=True, store=True, index=True, readonly=True, tracking=True,
        default="entry", change_default=True, related="move_id.move_type")

    
    @api.depends("discount_amount")
    def _compute_discount_allowance(self):
        for inv in self:
            inv.discount_allowance = False
            if inv.discount_amount > 0:
                inv.discount_allowance = True

    discount_allowance = fields.Boolean("Allowance (Discount)", compute="_compute_discount_allowance")

    @api.constrains("discount")
    def validate_discount_percent(self):
        for line in self:
            if line.discount > 99:
                raise ValidationError(_("Discount percent cannot be greater than 99%"))



class Partner(models.Model):
    _inherit = 'res.partner'

    @api.depends('identities_ids')
    def _compute_identity_vals(self):
        for partner in self:
            seven_hundred_number = str()
            for identity in partner.identities_ids:
                if identity.id_type == '4':
                    seven_hundred_number = identity.id_number
            partner.update({
                    'seven_hundred_number':seven_hundred_number,
                })

    vat = fields.Char("VAT")
    # Customer Information Related Fields..
    cr_number = fields.Char("CR Number")
    seven_hundred_number = fields.Char("700 Number", compute="_compute_identity_vals")
    group_vat_reg = fields.Char("Group VAT Registration Number")
    identities_ids = fields.One2many('res.partner.identity', 'partner_id', string='Identity Lines', copy=True, auto_join=True)
    
    building_number = fields.Char("Building Number", required=True)
    district = fields.Char("District", required=True)
    city = fields.Char(required=True)
    additional_number = fields.Char("Additional No.", required=True, size=4)
    zip = fields.Char(required=True, size=5)
    neighborhood = fields.Char()

    def get_other_ids(self):
        """
        """
        if self.identities_ids:
            if len(self.identities_ids) <= 2:
                return ','.join([x.id_number for x in self.identities_ids])
            else:
                return ','.join([x.id_number for x in self.identities_ids[:2]])
        return str()

class PartnerIdentities(models.Model):
    
    _name = 'res.partner.identity'
    _description = "Partner Identity"
    
    id_type = fields.Selection([
            ("1", "National ID"), 
            ("2", "IQAMA"),
            ("3", "Passport ID"),
            ("4", "700 number"),
            ("5", "Tax Identification Number (TIN)"),
            ("6", "Commercial Registration (CR)"),
            ("7", "MOMRA License"),
            ("8", "MLSD License"),
            ("9", "SAGIA License"),
            ("10", "Other ID"),
        ], "ID Type", required=True)
    id_number = fields.Char("ID Number",required=True)
    partner_id = fields.Many2one('res.partner', string='Partner Reference', required=True, ondelete='cascade', index=True, copy=False)

class Company(models.Model):

    _inherit = 'res.company'

    group_vat_reg = fields.Char("Group VAT Registration Number")
    identities_ids = fields.One2many('res.company.identity', 'company_id', string='Identity Lines', copy=True, auto_join=True)
    building_number = fields.Char("Building Number", required=True)
    district = fields.Char("District", required=True)
    additional_number = fields.Char("Additional No.", required=True, size=4)
    city = fields.Char(required=True)
    zip = fields.Char(required=True, size=5)
    state_id = fields.Many2one('res.country.state', required=True)
    neighborhood = fields.Char(required=True)
    mobile = fields.Char()
    vat = fields.Char(required=True)
    einv_report_format = fields.Selection([('format_1', 'Report Layout 1'), ('format_2', 'Report Layout 2'), ('format_3', 'Report Layout 3'), ('format_4', 'Report Layout 4')], string="E-Invoice Report Format", default="format_1", required=True)

    def get_other_ids(self):
        """
        """
        if self.identities_ids:
            if len(self.identities_ids) <= 2:
                return ','.join([x.id_number for x in self.identities_ids])
            else:
                return ','.join([x.id_number for x in self.identities_ids[:2]])
        return str()

class CompanyIdentities(models.Model):
    
    _name = 'res.company.identity'
    _description = "Company Identity"
    
    id_type = fields.Selection([
            ("1", "National ID"), 
            ("2", "IQAMA"),
            ("3", "Passport ID"),
            ("4", "700 number"),
            ("5", "Tax Identification Number (TIN)"),
            ("6", "Commercial Registration (CR)"),
            ("7", "MOMRA License"),
            ("8", "MLSD License"),
            ("9", "SAGIA License"),
            ("10", "Other ID"),
        ], "ID Type")
    id_number = fields.Char("ID Number")
    company_id = fields.Many2one('res.company', string='Company Reference', required=True, ondelete='cascade', index=True, copy=False)


class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'
    
    def reverse_moves(self):
        self.ensure_one()
        moves = self.move_ids
        # Create default values.
        default_values_list = []
        for move in moves:
            reversal_data_vals = self._prepare_default_reversal(move)
            reversal_data_vals.update({
                    'debit_credit_note_reason':self.reason,
                })
            default_values_list.append(reversal_data_vals)

        batches = [
            [self.env['account.move'], [], True],   # Moves to be cancelled by the reverses.
            [self.env['account.move'], [], False],  # Others.
        ]
        for move, default_vals in zip(moves, default_values_list):
            is_auto_post = bool(default_vals.get('auto_post'))
            is_cancel_needed = not is_auto_post and self.refund_method in ('cancel', 'modify')
            batch_index = 0 if is_cancel_needed else 1
            batches[batch_index][0] |= move
            batches[batch_index][1].append(default_vals)


        # Handle reverse method.
        moves_to_redirect = self.env['account.move']
        for moves, default_values_list, is_cancel_needed in batches:
            new_moves = moves._reverse_moves(default_values_list, cancel=is_cancel_needed)

            if self.refund_method == 'modify':
                moves_vals_list = []
                for move in moves.with_context(include_business_fields=True):
                    moves_vals_list.append(move.copy_data({'date': self.date if self.date_mode == 'custom' else move.date})[0])
                new_moves = self.env['account.move'].create(moves_vals_list)

            moves_to_redirect |= new_moves

        self.new_move_ids = moves_to_redirect

        # Create action.
        action = {
            'name': _('Reverse Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        if len(moves_to_redirect) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': moves_to_redirect.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', moves_to_redirect.ids)],
            })
        return action


class AccountDebitNote(models.TransientModel):
    """
    Add Debit Note wizard: when you want to correct an invoice with a positive amount.
    Opposite of a Credit Note, but different from a regular invoice as you need the link to the original invoice.
    In some cases, also used to cancel Credit Notes
    """
    _inherit = 'account.debit.note'

    def create_debit(self):
        self.ensure_one()
        new_moves = self.env['account.move']
        for move in self.move_ids.with_context(include_business_fields=True): #copy sale/purchase links
            default_values = self._prepare_default_values(move)
            default_values.update({
                    'debit_credit_note_reason':self.reason,
                })
            new_move = move.copy(default=default_values)
            move_msg = _(
                "This debit note was created from:") + " <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>" % (
                       move.id, move.name)
            new_move.message_post(body=move_msg)
            new_moves |= new_move

        action = {
            'name': _('Debit Notes'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            }
        if len(new_moves) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': new_moves.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', new_moves.ids)],
            })
        return action
