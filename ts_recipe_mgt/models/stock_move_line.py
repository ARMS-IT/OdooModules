# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    def set_recipe_product(self):
        stock_invt = self.env['stock.inventory'].search([])
        for stock in stock_invt:
            st_pd_list = []
            if stock.sale_order_id:
                ol_pd_list = []
                for spd in stock.product_ids:
                    st_pd_list.append(spd.id)
                order_lines = stock.sale_order_id.order_line
                for pd in order_lines:
                    if pd.product_id.product_tmpl_id.is_recipe:
                        for t in pd.product_id.product_tmpl_id.recipe_structure_ids:
                            ol_pd_list.append(t.product_id.id)
                        st_pd_list.sort()
                        ol_pd_list.sort()
                        if st_pd_list == ol_pd_list:
                            stock.parent_product_id = pd.product_id.product_tmpl_id
                        print("^^^^^^^^^^^^^^^^^^^^^")
            if stock.pos_order_id:
                print("Stock id is *********** ",stock)
                move_ids = stock.move_ids
                pos_pd_list = []
                for spd in stock.product_ids:
                    st_pd_list.append(spd.id)
                pos_lines = stock.pos_order_id.lines
                for pd in pos_lines:
                    if pd.product_id.product_tmpl_id.is_recipe:
                        for t in pd.product_id.product_tmpl_id.recipe_structure_ids:
                            pos_pd_list.append(t.product_id.id)
                        st_pd_list.sort()
                        pos_pd_list.sort()
                        if st_pd_list == pos_pd_list:
                            stock.parent_product_id = pd.product_id.product_tmpl_id
                for mv in move_ids:
                    print("Move id is ~~~~~~~~~~~~ ",mv)
                    for mv_line in mv.move_line_ids:
                        
                        valuation_layers = mv_line.move_id.stock_valuation_layer_ids
                        cost = sum(valuation_layers.mapped(lambda svl: svl.unit_cost if svl.quantity > 0 else -svl.unit_cost))
                        mv_line.unit_cost = cost
                        mv_line.value = cost * mv_line.qty_done
                        print("Move Line id is ~~~~~~~~~~~~ ",mv_line)
                        mv_line.parent_product_id = stock.parent_product_id
                        mv_line.pos_order_id = stock.pos_order_id
                        mv_line.pos_session_id = stock.pos_session_id
                        
                print("^^^^^^^^^^^^^^^^^^^^^")
        pos_orders = self.env['pos.order'].search([])
        for pol in pos_orders.lines:
            if not pol.product_id.product_tmpl_id.is_recipe:
                if pol.order_id.picking_id:
                    picking_lines = pol.order_id.picking_id.move_line_ids_without_package
                    print("8888888")
                    for pl in picking_lines:
                        # if pd.product_id == pl.product_id:
                        valuation_layers = pl.move_id.stock_valuation_layer_ids
                        cost = sum(valuation_layers.mapped(lambda svl: svl.unit_cost if svl.quantity > 0 else -svl.unit_cost))
                        pl.unit_cost = cost
                        pl.value = cost * pl.qty_done
                        # stored_pd_cost += pl.value
                 
    
    api.depends('pos_order_id','pos_session_id')
    def compute_unitcost_product(self):
        for move_line in self:
            if move_line.state == 'done':
                valuation_layers = move_line.move_id.stock_valuation_layer_ids
                cost = sum(valuation_layers.mapped(lambda svl: svl.unit_cost if svl.quantity > 0 else -svl.unit_cost))
                move_line.unit_cost = cost
                move_line.value = cost * move_line.qty_done
            else:
                move_line.unit_cost = 0
                move_line.value = 0
        return

    # quantity = fields.Float('Quantity', digits=0, help='Quantity', readonly=True)
    uom_id = fields.Many2one(related='product_id.uom_id', readonly=True)
    unit_cost = fields.Float(compute='compute_unitcost_product',string='Unit Value', store=True)
    value = fields.Float('Total Value')
    # remaining_qty = fields.Float(digits=0, readonly=True)
    parent_product_id = fields.Many2one('product.template',string="Recipe Product")
    sale_order_id = fields.Many2one('sale.order',string="Order")
    pos_order_id = fields.Many2one('pos.order',string="Order")
    pos_session_id = fields.Many2one('pos.session', string="Session")
    
    
    # def create(self, vals):
    #     # move_id = vals['move_id']
    #     for f in vals:
    #         print('Printing vals +++++++++ ',f['move_id'])#['move_id'])
    #         move_id = self.env['stock.move'].browse(f['move_id'])
    #         valuation_layers = move_id.stock_valuation_layer_ids
    #         cost = sum(valuation_layers.mapped(lambda svl: svl.unit_cost if svl.quantity > 0 else -svl.unit_cost))
    #         print('Printing Cost +++++++++ ',cost)#['move_id'])
    #     # vals['unit_cost'] = cost
    #     # vals['value'] = cost * vals['qty_done']
    #     res = super(StockMoveLine, self).create(vals)
    #     return res
    
class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    _description = "Inventory Line"
    
    def _get_move_values(self, qty, location_id, location_dest_id, out):
        self.ensure_one()
        return {
            'name': _('INV:') + (self.inventory_id.name or ''),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': qty,
            'date': self.inventory_id.date,
            'company_id': self.inventory_id.company_id.id,
            'inventory_id': self.inventory_id.id,
            'state': 'confirmed',
            'restrict_partner_id': self.partner_id.id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'move_line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'lot_id': self.prod_lot_id.id,
                'product_uom_qty': 0,  # bypass reservation here
                'product_uom_id': self.product_uom_id.id,
                'qty_done': qty,
                'package_id': out and self.package_id.id or False,
                'result_package_id': (not out) and self.package_id.id or False,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'owner_id': self.partner_id.id,
                'sale_order_id': self.inventory_id.sale_order_id.id,
                'pos_order_id': self.inventory_id.pos_order_id.id,
                'pos_session_id': self.inventory_id.pos_session_id.id,
                'parent_product_id': self.inventory_id.parent_product_id.id,
            })]
        }
        
        
class TSPosReport(models.TransientModel):
    _name = 'ts.pos.report'

    # report_type = fields.Selection([
    #     ("purchase_register", "Purchase Register"),
    #     ("purchase_issued", "List of PO's Issued"),
    #     ("grn", "List of GRN"),
    #     ("purchase_invoices", "List of Purchase Invoices"),
    # ], required=1)
    date_from = fields.Date('Date from')
    date_to = fields.Date('Date to')
    partner_ids = fields.Many2many('res.partner', string='Customers')
    product_ids = fields.Many2many('product.product', string='Products')
    pos_order_id = fields.Many2one('pos.order',string="Pos Order")
    company_id = fields.Many2one('res.company',string="Company")
    location_id = fields.Many2one('stock.location',string="Location")
    product_type = fields.Selection([
        ("consu", "Consumable"),
        ("service", "Service"),
        ("product", "Storable Product"),
    ])

    def generate_pos_report(self):
        data = {
            # 'report_type': self.report_type,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'product_ids': self.product_ids.ids,
            'partner_ids': self.partner_ids.ids,
            'pos_order_id': self.pos_order_id.id,
            'company_id': self.company_id.id,
            'location_id': self.location_id.id,
            'product_type': self.product_type,
        }
        return self.env.ref('ts_recipe_mgt.action_pos_gp_report_xlsx').report_action(self, data=data)

class PosReportXLSX(models.AbstractModel):
    _name = 'report.ts_recipe_mgt.pos_report'
    _inherit = 'report.report_xlsx.abstract'
    
    def _compute_pos_sale_profit_data(self, data):
        domain = [('order_id.state', 'not in', ('draft', 'cancel'))]#,('order_id','in',(4290,4326))]
        if data.get('date_from', False):
            domain.append(('order_id.date_order', '>=', data.get('date_from')))
        if data.get('date_to', False):
            domain.append(('order_id.date_order', '<=', data.get('date_to')))
        if data.get('product_ids', False):
            domain.append(('product_id', 'in', data.get('product_ids')))
        if data.get('partner_ids', False):
            domain.append(('order_id.partner_id', 'in', data.get('partner_ids')))
        if data.get('pos_order_id', False):
            domain.append(('order_id', '=', data.get('pos_order_id')))
        if data.get('company_id', False):
            domain.append(('order_id.company_id', '=', data.get('company_id')))
        if data.get('location_id', False):
            domain.append(('order_id.location_id', '=', data.get('location_id')))
        if data.get('product_type', False):
            domain.append(('product_id.type', '=', data.get('product_type')))
        

        pos_order_lines = self.env['pos.order.line'].search(domain)
        return pos_order_lines

    
    def generate_xlsx_report(self, workbook, data, records):
        company_id = self.env['res.company'].search([])[0]
        report_name = 'Pos Report'
        sheet = workbook.add_worksheet(report_name)
        bold = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#02064a', 'border': 1})
        bold.set_font_color('white')
        bold.set_border_color('white')
        bold.set_text_wrap()

        style1 = workbook.add_format({'bold': True, 'font_size': 11, 'fg_color': '#dfe4e4'})
        style2 = workbook.add_format({'bold': False, 'border': 1,})
        style2.set_border_color('918888')
        money = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'})
        date_format = workbook.add_format({'num_format': 'm/d/yyyy', 'border': 1})
        date_format.set_border_color('918888')
        money_bold = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'bold': True, 'border': 1, 'fg_color': '#abe5f2'})
        money_bold.set_border_color('918888')
        percent_bold = workbook.add_format({'num_format': '0.00%', 'bold': True, 'border': 1, 'fg_color': '#abe5f2'})
        percent_bold.set_border_color('918888')
        footer_bold = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'bold': True, 'fg_color': '#02064a', 'border': 1})
        footer_bold.set_font_color('white')
        footer_bold.set_border(6)
        footer_bold.set_border_color('white')
        footer_per_bold = workbook.add_format({'num_format': '0.00%', 'bold': True, 'border': 1, 'fg_color': '#02064a'})
        footer_per_bold.set_font_color('white')
        footer_per_bold.set_border(6)
        footer_per_bold.set_border_color('white')
        money_style1 = workbook.add_format({'num_format': '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)', 'bold': True, 'fg_color': '#c6d9f0'})
        row = 1
        title_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#02064a', 'font_size': 16})
        title_format.set_font_color('white')
        title_format.set_border(6)
        title_format.set_border_color('white')
        sheet.set_row(0, 35)
        sheet.set_row(3, 24)
        # sheet.set_row(4, 23)
        sheet.merge_range('A1:N1', 'POS Gross Profit Report', title_format)
        sheet.merge_range('A4:E4', 'General Information' , bold)
        sheet.merge_range('F4:J4', 'Sales Price ', bold)
        sheet.merge_range('K4:L4', 'Cost', bold)
        sheet.merge_range('M4:M5', 'Gross Profit', bold)
        sheet.merge_range('N4:N5', 'Margin', bold)
        row += 2
        sheet.write(1, 0, 'Date From', style2)
        sheet.write(1, 1, data.get('date_from', ''), style2)
        sheet.write(2, 0, 'Date To', style2)
        sheet.write(2, 1, data.get('date_to', ''), style2)
        if data.get('company_id', False):
            sheet.write(1, 3, 'POS Name', style2)
            company_id = self.env['res.company'].search([('id','=',data.get('company_id'))])
            sheet.write(1, 4, company_id.name, style2)
        
        col = 0
        row += 1
        
        self._generate_pos_profit_report(sheet, data, row, col, bold, date_format, style2, money_bold, footer_bold, percent_bold, footer_per_bold)
    
    def _generate_pos_profit_report(self, sheet, data, row, col, bold, date_format, style2, money_bold, footer_bold, percent_bold, footer_per_bold):
        sheet.set_column('A:F', 16)
        sheet.set_column('G:G', 10)
        sheet.set_column('H:O', 16)
        sheet.write(row, col, 'POS Order No', bold)
        sheet.write(row, col + 1, 'Product', bold)
        sheet.write(row, col + 2, 'Customer', bold)
        sheet.write(row, col + 3, 'Pos Name', bold)
        # sheet.write(row, col + 4, 'Location', bold)
        sheet.write(row, col + 4, 'Date', bold)
        sheet.write(row, col + 5, 'Qty', bold)
        sheet.write(row, col + 6, 'Unit Price', bold)
        sheet.write(row, col + 7, 'Discount', bold)
        sheet.write(row, col + 8, 'Taxes', bold)
        sheet.write(row, col + 9, 'Total', bold)
        sheet.write(row, col + 10, 'Direct Product Cost', bold)
        sheet.write(row, col + 11, 'Recipe Consumption Cost', bold)
        # sheet.write(row, col + 12, 'Gross Profit', bold)

        row += 1
        order_lines = self._compute_pos_sale_profit_data(data)
        for order_line in order_lines:
            order_date = order_line.order_id.date_order or ''
            order_no = str(order_line.order_id.name) or ''
            pos_name = str(order_line.order_id.session_id.config_id.name) or ''
            # location_id = str(order_line.order_id.location_id.name) or ''
            customer = str(order_line.order_id.partner_id.name) or ''
            product = str(order_line.product_id.display_name)
            disc = 0
            if order_line.discount > 0 :
                disc =(order_line.price_unit * order_line.qty * order_line.discount)/100
            
            recipe_cons_cost = 0
            stored_pd_cost = 0
            if order_line.product_id.product_tmpl_id.is_recipe:
                mv_line_ids = self.env['stock.move.line'].search([('pos_order_id', '=', order_line.order_id.id),('parent_product_id','=',order_line.product_id.product_tmpl_id.id)])
                for pd in mv_line_ids:
                    # pd.compute_unitcost_product()
                    recipe_cons_cost += pd.value
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            # location_id = ''
            if order_line.order_id.session_id.picking_ids:
                if not order_line.product_id.product_tmpl_id.is_recipe:
                    for pick in order_line.order_id.session_id.picking_ids:
                        picking_lines = pick.move_line_ids_without_package
                        # location_id = str(pick.location_id.name) or ''
                        # picking_lines = order_line.order_id.picking_id.move_line_ids_without_package
                    for pl in picking_lines:
                        # pl.compute_unitcost_product()
                        if order_line.product_id == pl.product_id:
                            stored_pd_cost += pl.unit_cost*order_line.qty
                    print("***********************")
                        
            sheet.write(row, col, order_no, style2)
            sheet.write(row, col+1, product, style2)
            sheet.write(row, col+2, customer, style2)
            sheet.write(row, col+3, pos_name, style2)
            # sheet.write(row, col+4, location_id, style2)
            sheet.write(row, col+4, order_date, date_format)
            sheet.write(row, col+5, order_line.qty, money_bold)
            sheet.write(row, col+6, order_line.price_unit, money_bold)
            sheet.write(row, col+7, float(disc), money_bold)
            sheet.write(row, col+8, order_line.price_subtotal_incl - order_line.price_subtotal, money_bold)
            sheet.write(row, col+9, order_line.price_subtotal, money_bold)
            sheet.write(row, col+10, (stored_pd_cost*-1), money_bold)
            # sheet.write(row, col+10, (order_line.product_id.standard_price * order_line.qty), money_bold)
            sheet.write(row, col+11, (recipe_cons_cost*-1), money_bold)
            sheet.write_formula(row, col+12, f'=J{row+1}-K{row+1}-L{row+1}',money_bold)
            sheet.write_formula(row, col+13, f'=M{row+1}/J{row+1}', percent_bold )
            row += 1
        
        sheet.set_row(row, 8)
        sheet.merge_range(f"A{row+2}:E{row+2}", "TOTAL", bold)
        sheet.write_formula(row+1, 5, f'=SUM(F6:F{row})',footer_bold)
        sheet.write(row+1, 6, '',footer_bold)
        sheet.write_formula(row+1, 7, f'=SUM(H6:H{row})',footer_bold)
        sheet.write_formula(row+1, 8, f'=SUM(I6:I{row})',footer_bold)
        sheet.write_formula(row+1, 9, f'=SUM(J6:J{row})',footer_bold)
        sheet.write_formula(row+1, 10, f'=SUM(K6:K{row})',footer_bold)
        sheet.write_formula(row+1, 11, f'=SUM(L6:L{row})',footer_bold)
        sheet.write_formula(row+1, 12, f'=SUM(M6:M{row})',footer_bold)
        sheet.write_formula(row+1, 13, f'=M{row+2}/J{row+2}',footer_per_bold)


