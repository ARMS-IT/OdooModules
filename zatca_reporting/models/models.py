# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api

class ZatcaReporting(models.TransientModel):
    
    _name = "account.invoice.zatca.report"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    status = fields.Selection([('draft', 'Draft'), ('posted','Posted'), ('cancel','Cancel')], default="draft", required=True)
    product_ids = fields.Many2many("product.product", string="Products", required=False)
    all_products = fields.Boolean("All Products?")
    report_type = fields.Selection([('pdf','Pdf'), ('xls','Excel')], required=True, default="pdf")

    def generate_zatca_report(self):
        """
        """
        domain = [('invoice_type','=', 'vat'), ('state','=', self.status)]
        invoices = self.env['account.move'].sudo().search(domain)
        result = list()

        # Filter Invoices by date
        for invoice in invoices:
            for invoice_line in invoice.invoice_line_ids:
                if self.all_products:
                    result.append({'client_name': invoice.partner_id.name,'tax_number': invoice.partner_id.vat,'cr_number':invoice.partner_id.cr_number,'name':invoice_line.name,'number':invoice.name, 'date':invoice.invoice_time.date() if invoice.invoice_time else "", 'total':invoice_line.price_total})
                else:
                    if invoice_line.product_id.id in self.product_ids.ids:
                        result.append({'client_name': invoice.partner_id.name,'tax_number': invoice.partner_id.vat,'cr_number':invoice.partner_id.cr_number,'name':invoice_line.name,'number':invoice.name, 'date':invoice.invoice_time.date() if invoice.invoice_time else "", 'total':invoice_line.price_total})
        data = {
            'invoice_data': result
        }

        if self.report_type == 'pdf':
            return self.env.ref('zatca_reporting.action_report_zatca_invoicing').report_action(docids=invoices, data=data)
        elif self.report_type == 'xls':
            return self.env.ref('zatca_reporting.action_zatca_reporting_xlsx_report').report_action(docids=invoices, data=data)

class ZatcaReportingXlsxReport(models.AbstractModel):
    _name = 'report.zatca_reporting.zatca_reporting_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):

        data = json.loads(data.get('options_data'))
        sheet = workbook.add_worksheet('Zatca Reporting')
        bold = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#fffbed', 'border': True})
        title = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 20, 'bg_color': '#f2eee4', 'border': True})
        header_row_style = workbook.add_format({'bold': True, 'font_size': 10,'align': 'center', 'border': True})
        data_row_style = workbook.add_format({'font_size': 8, 'border': True})

        sheet.merge_range('A1:H1', 'Zatca Invoices Reporting', title)

        row = 3
        col = 0

        # Header row
        sheet.set_column(0, 5, 25)
        sheet.write(row, col, 'Client Name', header_row_style)
        sheet.write(row, col+1, 'Tax Identification Number', header_row_style)
        sheet.write(row, col+2, 'Commercial Registration Number', header_row_style)
        sheet.write(row, col+3, 'Invoice Number', header_row_style)
        sheet.write(row, col+4, 'Invoice Issuance Date', header_row_style)
        sheet.write(row, col+5, 'Invoice Total (VAT Inclusive)', header_row_style)
        sheet.write(row, col+6, 'Service  Description', header_row_style)
        sheet.write(row, col+7, 'Notes', header_row_style)

        row += 2
        if data.get('invoice_data'):
            for inv_line in data.get('invoice_data'):
                sheet.write(row, col, inv_line.get('client_name'), data_row_style)
                sheet.write(row, col+1, inv_line.get('tax_number'), data_row_style)
                sheet.write(row, col+2, inv_line.get('cr_number'), data_row_style)
                sheet.write(row, col+3, inv_line.get('number'), data_row_style)
                sheet.write(row, col+4, inv_line.get('date'), data_row_style)
                sheet.write(row, col+5, inv_line.get('total'), data_row_style)
                sheet.write(row, col+6, inv_line.get('name'), data_row_style)
                sheet.write(row, col+7, "", data_row_style)
                row += 1