# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Partner(models.Model):
    _inherit = 'res.partner'

    partner_code = fields.Char("Partner Code")

    def name_get(self):
        res = []
        for part in self:
            name = part.name
            if part.partner_code:
                name = '%s - %s' % (part.partner_code,name)
            res.append((part.id, name))
        return res
        return super(Partner, self).name_get()

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        if args is None:
            args = []
        domain = args + ['|', ('partner_code', operator, name), ('name', operator, name)]
        return self._search(domain, limit=limit, access_rights_uid=name_get_uid)
