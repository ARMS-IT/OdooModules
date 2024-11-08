# -*- coding: utf-8 -*-
# Copyright 2020-2021 Artem Shurshilov
# Odoo Proprietary License v1.0

# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT file).

# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).

# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.

# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class ir_attachment_tag(models.Model):
    _name = 'ir.attachment.tag'
    _parent_store = True

    name = fields.Char('Tag Name', required=True, translate=True)
    active = fields.Boolean(
        help='The active field allows you to hide the tag without removing it.', default=True)
    parent_id = fields.Many2one(
        string='Parent Tag', comodel_name='ir.attachment.tag', index=True, ondelete='cascade')
    child_id = fields.One2many(
        string='Child Tags', comodel_name='ir.attachment.tag', inverse_name='parent_id')
    parent_path = fields.Char(index=True)
    image = fields.Binary('Image')

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists!"),
    ]

    #@api.multi
    def name_get(self):
        """ Return the tags' display name, including their direct parent. """
        res = {}
        for record in self:
            current = record
            name = current.name
            while current.parent_id:
                name = '%s / %s' % (current.parent_id.name, name)
                current = current.parent_id
            res[record.id] = name

        return [(record.id,  record.name) for record in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        tags = self.search(args, limit=limit)
        return tags.name_get()


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    tag_ids = fields.Many2many(string='Tags',
                               comodel_name='ir.attachment.tag',
                               relation='ir_attachment_tag_rel',
                               column1='tag_id',
                               column2='attachment_id')
    category_id = fields.Many2one(
        comodel_name="ir.attachment.category",
        string="Category",
    )
    number = fields.Char('Number', readonly=True)

    def _read_group_allowed_fields(self):
        return ['type', 'company_id', 'res_id', 'create_date', 'create_uid', 'name', 'mimetype', 'id', 'url', 'res_field', 'res_model', 'tag_ids', 'category_id']

    def _check_groups_access(self, groups_ids):
        for group in groups_ids:
            external_id = group.get_external_id()[group.id]
            if not self.env.user.has_group(str(external_id)):
                raise ValidationError(
                    """Your user's access groups are not included in the list of allowed \n
                    access groups for these attachments, contact your administrator""")

    def create(self, vals):
        res = super(IrAttachment, self).create(vals)
        if res.res_model:
            # find category by model
            category_id = self.env['ir.attachment.category'].sudo().search([
                ('model_id', '=', res.res_model)
            ], limit=1)
            if category_id:
                self._check_groups_access(category_id.group_ids)
                res.category_id = category_id.id
            res.number = self.env['ir.sequence'].next_by_code(
                'advance_contract.contract')
        return res

    def write(self, vals):
        if self.res_model:
            # find category by model
            category_id = self.env['ir.attachment.category'].sudo().search([
                ('model_id', '=', self.res_model)
            ], limit=1)
            if category_id:
                self._check_groups_access(category_id.group_ids)
                vals['category_id'] = category_id.id
            vals['number'] = self.env['ir.sequence'].next_by_code(
                'advance_contract.contract')
        return super(IrAttachment, self).write(vals)

    def download_filter(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document_ids?ids='+str(self.ids).replace(' ', ''),
        }
