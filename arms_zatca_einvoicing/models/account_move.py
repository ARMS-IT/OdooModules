# -*- coding: utf-8 -*-

import os
import json
import pytz
import hashlib
import base64
import qrcode, math
from datetime import date,datetime
from io import BytesIO
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.http import request
from odoo.addons.ehcs_qr_code_base.models.qr_code_base import generate_qr_code
import uuid
from odoo.exceptions import ValidationError,UserError
import codecs
from .fatoorah import Fatoora
from .xml_generator import generate_einvoice_xml
import pytz
from .csr_config import CSR_CONFIG
from requests.structures import CaseInsensitiveDict
import logging
_logger = logging.getLogger(__name__)


# SANDBOX CREDENTIALS : 
ZATCA_SB_CSID_BINARY_SECURITY_TOKEN = "TUlJRDFEQ0NBM21nQXdJQkFnSVRid0FBZTNVQVlWVTM0SS8rNVFBQkFBQjdkVEFLQmdncWhrak9QUVFEQWpCak1SVXdFd1lLQ1pJbWlaUHlMR1FCR1JZRmJHOWpZV3d4RXpBUkJnb0praWFKay9Jc1pBRVpGZ05uYjNZeEZ6QVZCZ29Ka2lhSmsvSXNaQUVaRmdkbGVIUm5ZWHAwTVJ3d0dnWURWUVFERXhOVVUxcEZTVTVXVDBsRFJTMVRkV0pEUVMweE1CNFhEVEl5TURZeE1qRTNOREExTWxvWERUSTBNRFl4TVRFM05EQTFNbG93U1RFTE1Ba0dBMVVFQmhNQ1UwRXhEakFNQmdOVkJBb1RCV0ZuYVd4bE1SWXdGQVlEVlFRTEV3MW9ZWGxoSUhsaFoyaHRiM1Z5TVJJd0VBWURWUVFERXdreE1qY3VNQzR3TGpFd1ZqQVFCZ2NxaGtqT1BRSUJCZ1VyZ1FRQUNnTkNBQVRUQUs5bHJUVmtvOXJrcTZaWWNjOUhEUlpQNGI5UzR6QTRLbTdZWEorc25UVmhMa3pVMEhzbVNYOVVuOGpEaFJUT0hES2FmdDhDL3V1VVk5MzR2dU1ObzRJQ0p6Q0NBaU13Z1lnR0ExVWRFUVNCZ0RCK3BId3dlakViTUJrR0ExVUVCQXdTTVMxb1lYbGhmREl0TWpNMGZETXRNVEV5TVI4d0hRWUtDWkltaVpQeUxHUUJBUXdQTXpBd01EYzFOVGc0TnpBd01EQXpNUTB3Q3dZRFZRUU1EQVF4TVRBd01SRXdEd1lEVlFRYURBaGFZWFJqWVNBeE1qRVlNQllHQTFVRUR3d1BSbTl2WkNCQ2RYTnphVzVsYzNNek1CMEdBMVVkRGdRV0JCU2dtSVdENmJQZmJiS2ttVHdPSlJYdkliSDlIakFmQmdOVkhTTUVHREFXZ0JSMllJejdCcUNzWjFjMW5jK2FyS2NybVRXMUx6Qk9CZ05WSFI4RVJ6QkZNRU9nUWFBL2hqMW9kSFJ3T2k4dmRITjBZM0pzTG5waGRHTmhMbWR2ZGk1ellTOURaWEowUlc1eWIyeHNMMVJUV2tWSlRsWlBTVU5GTFZOMVlrTkJMVEV1WTNKc01JR3RCZ2dyQmdFRkJRY0JBUVNCb0RDQm5UQnVCZ2dyQmdFRkJRY3dBWVppYUhSMGNEb3ZMM1J6ZEdOeWJDNTZZWFJqWVM1bmIzWXVjMkV2UTJWeWRFVnVjbTlzYkM5VVUxcEZhVzUyYjJsalpWTkRRVEV1WlhoMFoyRjZkQzVuYjNZdWJHOWpZV3hmVkZOYVJVbE9WazlKUTBVdFUzVmlRMEV0TVNneEtTNWpjblF3S3dZSUt3WUJCUVVITUFHR0gyaDBkSEE2THk5MGMzUmpjbXd1ZW1GMFkyRXVaMjkyTG5OaEwyOWpjM0F3RGdZRFZSMFBBUUgvQkFRREFnZUFNQjBHQTFVZEpRUVdNQlFHQ0NzR0FRVUZCd01DQmdnckJnRUZCUWNEQXpBbkJna3JCZ0VFQVlJM0ZRb0VHakFZTUFvR0NDc0dBUVVGQndNQ01Bb0dDQ3NHQVFVRkJ3TURNQW9HQ0NxR1NNNDlCQU1DQTBrQU1FWUNJUUNWd0RNY3E2UE8rTWNtc0JYVXovdjFHZGhHcDdycVNhMkF4VEtTdjgzOElBSWhBT0JOREJ0OSszRFNsaWpvVmZ4enJkRGg1MjhXQzM3c21FZG9HV1ZyU3BHMQ=="
ZATCA_SB_CSID_SECRET_KEY = "Xlj15LyMCgSC66ObnEO/qVPfhSbs3kDTjWnGheYhfSs="
ZATCA_SB_OTP = "123456"

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

CONFIG_FILE_NAME = 'zatca_vendor_config.txt'
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = "{}/{}".format(CURRENT_PATH, CONFIG_FILE_NAME)

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
        return self.env.ref('arms_zatca_einvoicing.zatca_account_invoices').report_action(self)


    def action_generate_report_a3(self):
        return self.env.ref('arms_zatca_einvoicing.zatca_account_invoices_a3').report_action(self)

    def convert_datetime_to_timestamp(self):
        """
        """
        invoice_timestamp = 0
        if self.invoice_time:
            invoice_timestamp = datetime.timestamp(self.invoice_time)
        return invoice_timestamp

    def convert_datetime_to_iso(self):
        """
        """
        invoice_time_iso = str()
        if self.invoice_time:
            from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
            DEFAULT_SERVER_DATETIME_FORMAT = DEFAULT_SERVER_DATETIME_FORMAT.replace(' ','T')
            if self.env.user.tz:
                tz = pytz.timezone(self.env.user.tz) or pytz.utc
                invoice_time = pytz.utc.localize(self.invoice_time).astimezone(tz)
            else:
                invoice_time = self.invoice_time
            invoice_time_iso = invoice_time.strftime("{}Z".format(DEFAULT_SERVER_DATETIME_FORMAT))
        return invoice_time_iso

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
            
            # qr_invoice_time = move.convert_datetime_to_timestamp()
            qr_invoice_time = move.convert_datetime_to_iso()
            qr_amount_total = move.amount_total
            qr_tax_total = move.amount_tax
            
            # assign values
            move.qr_seller_name = qr_seller_name
            move.qr_seller_vat = qr_seller_vat
            move.qr_invoice_time = qr_invoice_time
            move.qr_amount_total = qr_amount_total
            move.qr_tax_total = qr_tax_total
            move.get_qr_string()
            base_domain = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
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
    journal_type = fields.Selection("Journal Type", related="journal_id.type")    


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
    draft_check = fields.Boolean(string="Check Draft", help="If already posted not allow to edit")
    is_acknowledged = fields.Boolean("Acknowledged")

    business_process_type = fields.Text("Business Process Type", required=True, default="reporting:1.0")


    def update_invoicetime(self):
    	invoice_src = self.env['account.move'].search([('invoice_time', '=', False),('state', '!=', 'draft'),('journal_type', '!=', 'general')])
#    	invoice_src = self.env['account.move'].search([('id', '=', 17)])
#    	raise UserError(f"DATE {invoice_src}.")
    	cursor = self._cr
    	for invoice_id in invoice_src:
    		if invoice_id:
    			_logger.info(f"************* invoice_id: {invoice_id}*************")
    			cursor.execute("select date,create_date from account_move where id = %s ", ([invoice_id.id]))
    			result = cursor.fetchall()
    			date = result[0][0]    			
    			time_str = str(result[0][1])
    			time = time_str[11:19]    			
    			invoice_time = str(date) + ' ' + str(time)
    			inv_time = datetime.strptime(str(invoice_time),"%Y-%m-%d %H:%M:%S")
    			invoice_id.invoice_time = inv_time
    			#2022-11-16 13:10:50.829956
    			_logger.info(f"************* DATe: {inv_time}*************")
    			_logger.info(f"************* TIME: {inv_time}*************")
    			#raise UserError(f"DATE {xxx}")
    	return True        


    def action_post(self):
        res = super(AccountMove, self).action_post()
        for moves in self:
            if moves.move_type in ('out_invoice','out_refund','in_refund','in_invoice'):
                moves.draft_check = True
            else:
                moves.draft_check = False
        return res        

    def _compute_xml_json_str(self):
        """
        """
        for move in self:
            res = dict()
            # res["UBLExtensions"] = [
            #     {
            #         "UBLExtension":{
            #             "ExtensionURI": "urn:oasis:names:specification:ubl:dsig:enveloped:xades",
            #             "ExtensionContent":{
            #                 "UBLDocumentSignatures":{
            #                     "SignatureInformation":{
            #                         "ID":"urn:oasis:names:specification:ubl:signature:1",
            #                         "ReferencedSignatureID":"urn:oasis:names:specification:ubl:signature:Invoice",
            #                         "ds_Signature":{
            #                             "SignedInfo":{
            #                                 "CanonicalizationMethod":"",
            #                                 "ds_SignatureMethod":"",
            #                                 "Reference1":{
            #                                     "Transforms":{
            #                                         "Transform1":{
            #                                             "XPath":"not(//ancestor-or-self::ext:UBLExtensions)",
            #                                         },
            #                                         "Transform2":{
            #                                             "XPath":"not(//ancestor-or-self::cac:Signature)",
            #                                         },
            #                                         "Transform3":{
            #                                             "XPath":"not(//ancestor-or-self::cac:AdditionalDocumentReference[cbc:ID='QR'])",
            #                                         },
            #                                         "Transform4":{
            #                                             "XPath":"not(//ancestor-or-self::ext:UBLExtensions)",
            #                                         },
            #                                         "Transform":"",
            #                                     },
            #                                     "DigestMethod":"",
            #                                     "DigestValue": "1234657981234567891234656789" #QUERY_XML,

            #                                 },
            #                                 "Reference2":{
            #                                     "DigestMethod":"",
            #                                     "DigestValue":"1234657981234567891234656789", #QUERY_XML,
            #                                 }
            #                             },
            #                             "SignatureValue":"1234657981234567891234656789", #QUERY_XML,
            #                             "KeyInfo":{
            #                                 "X509Data":{
            #                                     "X509Certificate": "1234657981234567891234656789" #Query XML
            #                                 }
            #                             },
            #                             "Object":{
            #                                 "QualifyingProperties":{
            #                                     "SignedProperties":{
            #                                         "SignedSignatureProperties":{
            #                                             "SigningTime":"2022-03-25T02:09:39Z", #QUERY_XML
            #                                             "SigningCertificate":{
            #                                                 "Cert":{
            #                                                     "CertDigest":{
            #                                                         "DigestMethod":"",
            #                                                         "DigestValue":"ZGNjZTk3MGIzYjg0M2FlODczNGIyMDQ3ZjczOTM2NjgyNjljYmQ4NGYyZThkOTlmY2ZjYTU0ODFhZWE3MjE4NA", #QUERY_XML
            #                                                     },
            #                                                     "IssuerSerial":{
            #                                                         "X509IssuerName":"CN=eInvoicing",
            #                                                         "X509SerialNumber":"1641728828389", #QUERY_XML
            #                                                     }
            #                                                 }
            #                                             }, #QUERY_XML
            #                                         }
            #                                     }
            #                                 }
            #                             }
            #                         }, 
            #                     }, 
            #                 }
            #             }
            #         }
            #     }
            # ]

            res["ProfileID"] = move.business_process_type
            res["ID"] = move.id
            res["UUID"] = move.uuid_number,
            res["IssueDate"] = move.invoice_time.date().strftime("%Y-%m-%d") if move.invoice_time else "",
            res["IssueTime"] = move.invoice_time.time().strftime("%H:%M:%S") if move.invoice_time else "",
            res["InvoiceTypeCode"] = move.invoice_type_code
            res["DocumentCurrencyCode"] = move.currency_id.name
            res["TaxCurrencyCode"] = move.currency_id.name
            res["LineCountNumeric"] = len(move.invoice_line_ids)
            if move.debit_origin_id:
                res['BillingReference'] = {
                    "InvoiceDocumentReference": {
                        "ID": move.debit_origin_id.id,
                    }
                }
            elif move.invoice_type_code == '381':
                res['BillingReference'] = {
                    "InvoiceDocumentReference": {
                        "ID": move.ref,
                    }
                }
            res["AdditionalDocumentReference-1"] = [{
                    "ID": "ICV", 
                    "UUID": move.id,
                }]
            res["AdditionalDocumentReference-2"] = [{
                    "ID": "PIH", 
                    "Attachment": {
                        "EmbeddedDocumentBinaryObject": move.previous_invoice_hash_number,
                    }
                }]
            res["AdditionalDocumentReference-3"] = [
                {
                    "ID": "QR",
                    "Attachment": {
                        "EmbeddedDocumentBinaryObject": move.qr_string,
                    }
                }
            ]

            res["Signature"] = [
                {
                    "ID": "urn:oasis:names:specification:ubl:signature:Invoice",
                    "SignatureMethod": "urn:oasis:names:specification:ubl:dsig:enveloped:xades",
                }
            ]
            
            vendor = move.company_id.partner_id
            if move.special_billing_agreement == 'third_party':
                vendor = move.vendor_id

            res["AccountingSupplierParty"] = [
                {
                    "Party": {
                        "PartyIdentification-MLS": vendor.vat, #vendor.identities_ids.filtered(lambda x:x.id_type == '5').id_number,
                        "PostalAddress": {
                            "StreetName": (vendor.street + vendor.street2) if vendor.street2 else vendor.street or "",
                            "BuildingNumber": vendor.building_number or "",
                            "PlotIdentification": vendor.additional_number or "",
                            "CitySubdivisionName": vendor.district or "",
                            "CityName": vendor.city or "",
                            "PostalZone": vendor.zip or "",
                            "CountrySubentity": vendor.country_id.name or "",
                            "Country": {
                                "IdentificationCode": vendor.country_id.code or "",
                            }
                        },
                        "PartyTaxScheme": {
                            "CompanyID": vendor.vat or "",
                            "TaxScheme": {
                                "ID": "VAT"
                            }
                        },
                        "PartyLegalEntity": {
                            "RegistrationName": vendor.name or "",
                        }
                    }
                },
            ]


            res["AccountingCustomerParty"] = [
                {
                    "Party": {
                        "PartyIdentification-SAG":move.partner_id.vat, #move.partner_id.identities_ids.filtered(lambda x:x.id_type == '5').id_number,
                        "PostalAddress": {
                            "StreetName": (move.partner_id.street + move.partner_id.street2) if move.partner_id.street2 else move.partner_id.street or "",
                            "BuildingNumber": move.partner_id.building_number or "",
                            "BuildingNumber": move.partner_id.building_number or "",
                            "PlotIdentification": move.partner_id.additional_number or "",
                            "CitySubdivisionName": move.partner_id.district or "",
                            "CityName": move.partner_id.city or "",
                            "PostalZone": move.partner_id.zip or "",
                            "CountrySubentity": move.partner_id.country_id.name or "",
                            "Country": {
                                "IdentificationCode": move.partner_id.country_id.code or ""
                            }
                        },
                        "PartyTaxScheme": {
                            # "CompanyID": move.partner_id.vat or "",
                            "TaxScheme": {
                                "ID": "VAT"
                            }
                        },
                        "PartyLegalEntity": {
                            "RegistrationName": move.partner_id.name or "",
                        }
                    }
                },
            ]

            res["Delivery"] = {
                "ActualDeliveryDate": move.supply_date.strftime("%Y-%m-%d") if move.supply_date else "",
                # "LatestDeliveryDate": move.supply_end_date.strftime("%Y-%m-%d") if move.supply_end_date else "",
            }
            res["PaymentMeans"] = {
                "PaymentMeansCode": move.payment_mean_id.code
            }
            if move.invoice_type_code in ['383', '381']:
                res['PaymentMeans']['InstructionNote'] = "Debit Note" if move.invoice_type_code == '383' else "Credit Note"
                
            TotalVat = round(sum(line.tax_amount for line in move.invoice_line_ids), 2)
            res["TaxTotal"] = [
                {
                    "TaxAmount": "%.2f" % TotalVat,
                    "TaxSubtotal": {
                        "TaxableAmount": "%.2f" % move.amount_untaxed,#--Subtotal
                        "TaxAmount": "%.2f" % TotalVat,
                        "TaxCategory": { #tODISCUSS
                            "ID": "S",
                            "Percent": 15,
                            "TaxScheme": {
                                "ID": "VAT"
                            }
                        }
                    }
                },
            ]
            res["TaxTotal-1"] = [
                {
                    "TaxAmount":  "%.2f" % round(sum(line.tax_amount for line in move.invoice_line_ids), 2),
                }
            ]
            LineExtensionAmount = round(sum(line.price_subtotal for line in move.invoice_line_ids), 2)
            TaxExclusiveAmount = round(sum(line.price_subtotal for line in move.invoice_line_ids), 2)
            TaxInclusiveAmount = round(TaxExclusiveAmount + TotalVat, 2)

            res["LegalMonetaryTotal"] = {
                "LineExtensionAmount":  "%.2f" % LineExtensionAmount,
                "TaxExclusiveAmount":  "%.2f" % TaxExclusiveAmount,
                "TaxInclusiveAmount": "%.2f" %  TaxInclusiveAmount,
                "AllowanceTotalAmount": 0,
                "PayableAmount":  "%.2f" % round(move.amount_total, 2),
            }
            invoice_lines = list()
            for line in move.invoice_line_ids:
                invoice_lines.append({
                    "ID": line.id,
                    "InvoicedQuantity":  "%.2f" % line.quantity,
                    "LineExtensionAmount":  "%.2f" % line.price_subtotal,
                    "TaxTotal": {
                        "TaxAmount":  "%.2f" % line.tax_amount,
                        "RoundingAmount":  "%.2f" % round(line.price_total+line.tax_amount, 2),
                    },
                    "Item": {
                        "Name": line.product_id.name,
                        "ClassifiedTaxCategory": [{
                            "ID": "S",
                            "Percent": int(tax_info.amount),
                            "TaxScheme": {
                                "ID": "VAT"
                            }
                        } for tax_info in line.tax_ids]
                    },
                    "Price": {
                        "PriceAmount":  "%.2f" % round(line.price_total+line.tax_amount, 2)
                    }
                })
            for line in invoice_lines:
                if not line.get('Item').get('ClassifiedTaxCategory'):
                    line.get('Item').pop('ClassifiedTaxCategory')

            for index, inv_line in enumerate(invoice_lines):
                res["InvoiceLine-{}".format(index+1)] = inv_line

            xml_json_str = json.dumps(res, indent=4)
            clean_xml_data = generate_einvoice_xml(res, len(invoice_lines))

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
            # import pdb;pdb.set_trace()
            if invoice.move_type == 'out_invoice':
                if invoice.debit_origin_id:
                    invoice.invoice_type_code = '383'
                else:
                    invoice.invoice_type_code = '388'
            
            elif invoice.move_type == 'out_refund':
                invoice.invoice_type_code = '381'

            elif invoice.move_type == 'in_refund':
                invoice.invoice_type_code = '383'

            elif invoice.move_type == 'in_invoice':
                invoice.invoice_type_code = '388'


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

    # @api.depends('invoice_time')
    # def _compute_invoice_date(self):
    #     for move in self:
    #         move.invoice_date = False
    #         if move.invoice_time:
    #             move.invoice_date = move.invoice_time.date()
    #             move.date = move.invoice_time.date()


    # Invoice Date (using Default)
    invoice_time = fields.Datetime("Invoice Time", default=False, tracking=True, required=False)
    # invoice_date = fields.Date(compute="_compute_invoice_date", store=True)
    # date = fields.Date(compute="_compute_invoice_date", store=True)
    supply_date = fields.Date("Supply Date", required=False)
    supply_end_date = fields.Date("Supply End Date", required=False)


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

    payment_mean_id = fields.Many2one('account.payment.mean', string="Payment Mean", default=lambda self:self.env.ref("arms_zatca_einvoicing.payment_mean_30").id, domain=[('code','in',[10, 30, 42, 48, 1])])
#    payment_mean_id = fields.Many2one('account.payment.mean', string="Payment Mean", domain=[('code','in',[10, 30, 42, 48, 1])])
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

    def get_invoice_time(self):
        if self.invoice_time:
            invoice_time = self.invoice_time.replace(microsecond=0)
            invoice_time = datetime.strptime(str(invoice_time), "%Y-%m-%d %H:%M:%S")
            tz = pytz.timezone(self.env.user.tz or "UTC")
            invoice_time = pytz.utc.localize(invoice_time).astimezone(tz)
            date = invoice_time.date()
            return date

    @api.model
    def create(self, vals):
        vals['uuid_number'] = uuid.uuid4()
        vals['invoice_hash_number'] = self.get_hash(vals.get('uuid_number'))
        #invoice_time = vals.get('invoice_time')
        #if invoice_time:
        #    vals['invoice_date'] = self.get_invoice_time(invoice_time)
        #    vals['date'] = self.get_invoice_time(invoice_time)
        res = super(AccountMove, self).create(vals)
        self.invoice_date = res.get_invoice_time()
        return res

    def onchange_invoice_time(self):
        if self.invoice_time:
            # tz = pytz.timezone(self.env.user.tz or "UTC")
            # invoice_time = self.invoice_time
            # invoice_time = pytz.utc.localize(invoice_time).astimezone(tz)
            date = self.get_invoice_time()
            self.invoice_date = date
            self.date = date


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
            self.payment_mean_id = self.env.ref("arms_zatca_einvoicing.payment_mean_30").id
        if self.invoice_type == 'vat':
            self.inv_payment_type = 'b2b-b2g'
            self.payment_mean_id = self.env.ref("arms_zatca_einvoicing.payment_mean_30").id

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


    ##############################################################################
    ## Integration Phase-2 Methods                                              ##
    ##############################################################################

    def _get_invoice_hash(self):
        """
        """
        cipher_text = base64.b64decode(self.invoice_xml_document).decode('utf-8')
        sha256_hash = hashlib.sha256()
        sha256_hash.update(cipher_text.encode())
        # print(sha256_hash.digest().hex())
        b64bytes_hex = base64.b64encode((sha256_hash.digest().hex()).encode())
        b64bytes_hex_string = b64bytes_hex.decode()
        b64bytes_digest = base64.b64encode(sha256_hash.digest())
        b64bytes_digest_string = b64bytes_digest.decode()
        
        return b64bytes_digest_string
        # self.digest_invoice_hash = b64bytes_digest_string
        # self.hex_invoice_hash = b64bytes_hex_string

    def get_ubl_lang(self):
        self.ensure_one()
        return self.partner_id.lang or "en_US"

    def action_post(self):
        """
        """
        res = super(AccountMove, self).action_post()
        name = self.name
        if self.invoice_type_code == '383':
            name = name.replace("EINV", "DRN")
        self.write({
                'invoice_time':datetime.now(),
                'name':name,
            })
        return res

    def action_clearance_api_test(self):
        """
        """
        self.ensure_one()
        assert self.move_type in ("out_invoice", "out_refund", "in_invoice", "in_refund")
        lang = self.get_ubl_lang()
        version = "2.1"

        current_company = self.company_id

        base64_xml_string = self.invoice_xml_document.decode()
        invoice_hash_digest = self._get_invoice_hash()

        if current_company.zatca_mode == "sandbox":
            binary_token_and_secret_key = f"{ZATCA_SB_CSID_BINARY_SECURITY_TOKEN}:{ZATCA_SB_CSID_SECRET_KEY}"

        elif current_company.zatca_mode == "production":
            binary_token_and_secret_key = \
                f"{current_company.zatca_production_binary_security_token}:{current_company.zatca_production_secret_key}"
    
        api_authorization_base64 = base64.b64encode(binary_token_and_secret_key.encode())
        api_authorization = api_authorization_base64.decode()
        
        CLEARANCE_API_URL = "https://gw-apic-gov.gazt.gov.sa/e-invoicing/developer-portal/invoices/clearance/single"

        # Headers for API
        headers = CaseInsensitiveDict()
        headers["accept"] = "application/json"
        headers["accept-language"] = "en"
        headers["Clearance-Status"] = "1"
        headers["Accept-Version"] = "V2"
        headers["Authorization"] = f"Basic {api_authorization}"
        headers["Content-Type"] = "application/json"

        # Data for API
        data = """{0} "invoiceHash": "{1}", "uuid": "{2}", "invoice": "{3}" {4} """
        data = data.format("{", invoice_hash_digest, self.uuid_number, base64_xml_string, "}")

        # Response Timeout for API
        timeout = 3

        # API Type
        verb = 'post'

        # Calling API
        import pdb;pdb.set_trace()
        api_resp_check = self.env['api.response.check']
        requests.post(url=CLEARANCE_API_URL, headers=headers, data=data, timeout=timeout)
        popup, api_response = api_resp_check.api_call(verb=verb, url=CLEARANCE_API_URL, headers=headers, data=data, timeout=timeout)
        if 'clearedInvoice' in api_response:
            if api_response["clearedInvoice"] is not None:
                self.cleared_invoice = api_response["clearedInvoice"]
                self.cleared_invoice_qrcode = self.cleared_invoice_qr_code()
        return popup
        ###############################################################################################################
        # End Function



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

    def _get_default_vendor_config(self):
        """
        """
        configs = CSR_CONFIG
        return configs

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
    einv_report_format = fields.Selection([('format_1', 'Report Layout 1'), ('format_2', 'Report Layout 2'), ('format_3', 'Report Layout 3'), ('format_4', 'Report Layout 4'), ('format_5', 'Report Layout 5')], string="E-Invoice Report Format", default="format_3", required=True)
    zatca_vendor_config = fields.Text("Zatca Vendor Configuration", default=lambda self:self._get_default_vendor_config())
    zatca_mode = fields.Selection([('sandbox','Sandbox'), ('production','Production')], default='sandbox')
    zatca_production_binary_security_token = fields.Text("Production Binary Security Token")
    zatca_production_secret_key = fields.Char("Production Secret Key")
    zatca_production_otp = fields.Char("Production OTP")

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

class AccountPayment(models.Model):

    _inherit = 'account.payment'

    @api.model
    def create(self, vals):
        res = super(AccountPayment, self).create(vals)
        return res

    def write(self, vals):
        res = super(AccountPayment, self).write(vals)
        return res


