# -*- coding: utf-8 -*-

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

class AccountTaxCode(models.Model):

    _name = 'account.tax.codes'

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", required=True)
    description = fields.Text(required=True)

    def name_get(self):
        name_list = []
        for record in self:
            name = "[{}] {}".format(record.code, record.name)
            name_list += [(record.id, name)]
        return name_list

class AccountTax(models.Model):

    _inherit = 'account.tax'

    code_id = fields.Many2one("account.tax.codes", string="Code")

