# -*- coding: utf-8 -*-

from odoo import models

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def get_payslip_pdf_url(self, suffix=None, report_type=None, download=None):
        self.ensure_one()
        url = '/my/payslip/report/%s?%s%s' % (
            self.id,
            'report_type=%s' % report_type if report_type else '',
            '&download=true' if download else ''
        )
        return url

    def _get_report_base_filename(self):
        self.ensure_one()
        return self.name
