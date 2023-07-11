import os
import re
import json
import base64
import inspect
import logging
import tempfile
import datetime
import traceback

import werkzeug
from werkzeug import urls
from werkzeug import utils
from werkzeug import exceptions
from werkzeug.urls import iri_to_uri

import odoo
from odoo import _
from odoo import api
from odoo import tools
from odoo import http
from odoo import models
from odoo import release
from odoo.http import request
from odoo.http import Response
from odoo.tools.misc import str2bool
from datetime import datetime

from odoo.http import  route

from odoo import fields
from datetime import timedelta

_logger = logging.getLogger(__name__)

REST_VERSION = {
    'server_version': release.version,
    'server_version_info': release.version_info,
    'server_serie': release.serie,
    'api_version': 2,
}

NOT_FOUND = {
    'error': 'unknown_command',
}

DB_INVALID = {
    'error': 'invalid_db',
}

FORBIDDEN = {
    'error': 'token_invalid',
    'code':'01'
}

NO_API = {
    'error': 'rest_api_not_supported',
}

LOGIN_INVALID = {
    'error': 'invalid_login',
}

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'

def abort(message, rollback=False, status=403):
    response = Response(json.dumps(message,
        sort_keys=True, indent=4, cls=ObjectEncoder),
        content_type='application/json;charset=utf-8', status=status) 
    if request._cr and rollback:
        request._cr.rollback()
    exceptions.abort(response)

def check_token():
    token = request.params.get('token') and request.params.get('token').strip()
    if not token:
        abort(FORBIDDEN)
    env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
    uid = env['rest.api.token'].check_token(token)
    if not uid:
        abort(FORBIDDEN)
    request._uid = uid
    request._env = api.Environment(request.cr, uid, request.session.context or {})

def check_token_trans(token):
    # token = request.params.get('token') and request.params.get('token').strip()
    token = token.strip()
    token_valid = True
    if not token:
        token_valid = False
        # abort_trans(FORBIDDEN)
        return token_valid
    env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
    uid = env['rest.api.token'].check_token(token)
    if not uid:
        token_valid = False
        # abort_trans(FORBIDDEN)
        return token_valid
    request._uid = uid
    request._env = api.Environment(request.cr, uid, request.session.context or {})
    return token_valid

def ensure_db():
    db = request.params.get('db') and request.params.get('db').strip()
    if db and db not in http.db_filter([db]):
        db = None
    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db
    if not db:
        db = http.db_monodb(request.httprequest)
    if not db:
        abort(DB_INVALID, status=404)
    if db != request.session.db:
        request.session.logout()
    request.session.db = db
    try:
        env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
#        module = env['ir.module.module'].search([['name', '=', "tanweel_rest_api"]], limit=1)
        module = env['ir.module.module'].search([['name', '=', "pos_alrashed"]], limit=1)
        if module.state != 'installed':
            abort(NO_API, status=500)
    except Exception as error:
        _logger.error(error)
        abort(DB_INVALID, status=404)

def check_params(params):
    missing = []
    for key, value in params.items():
        if not value:
            missing.append(key)
    if missing:
        abort({'error': "arguments_missing %s" % str(missing)}, status=400)

def check_params_trans(params):
    missing = []
    for key, value in params.items():
        if not value:
            missing.append(key)
    if missing:
        return {"param_valid":False,"status":"400","error": "arguments_missing %s" % str(missing)}
        # abort({'error': "arguments_missing %s" % str(missing)}, status=400)
    else:
        return {"param_valid":True}

class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)


class RESTController(http.Controller):

    #----------------------------------------------------------
    # General
    #----------------------------------------------------------

    @http.route('/api/<path:path>', auth="none", type='http', csrf=False)
    def api_catch(self, **kw):
        return Response(json.dumps(NOT_FOUND,
            sort_keys=True, indent=4, cls=ObjectEncoder),
            content_type='application/json;charset=utf-8', status=404)

    @http.route('/api', auth="none", type='http')
    def api_version(self, **kw):    
        return Response(json.dumps(REST_VERSION,
            sort_keys=True, indent=4, cls=ObjectEncoder),
            content_type='application/json;charset=utf-8', status=200)        
    
    
    @http.route([
        '/api/life',
        '/api/life/<string:token>'], auth="none", type='http', csrf=False)
    def api_life(self, token=None, **kw):
        check_params({'token': token})
        ensure_db()
        check_token()
        env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
        result = env['rest.api.token'].lifetime_token(token)
        return Response(json.dumps(result,
            sort_keys=True, indent=4, cls=ObjectEncoder),
            content_type='application/json;charset=utf-8', status=200) 
        
    @http.route('/api/close', auth="none", type='http', methods=['POST'], csrf=False)
    def api_close(self, token=None, **kw):
        check_params({'token': token})
        ensure_db()
        check_token()
        env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
        result = env['rest.api.token'].delete_token(token)
        return Response(json.dumps(result,
            sort_keys=True, indent=4, cls=ObjectEncoder),
            content_type='application/json;charset=utf-8', status=200) 
    
            
    #----------------------------------------------------------
    # Token Authentication
    #----------------------------------------------------------

    #tanweel API 1
    @http.route('/api/authenticate', type='http', auth='none', methods=['POST'], csrf=False)
    def api_authenticate(self, db=None, login=None, password=None, **kw):
        check_params({'db': db, 'login': login, 'password': password})
        ensure_db()
        uid = request.session.authenticate(db, login, password)
        if uid:
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
            token = env['rest.api.token'].generate_token(uid)
            return Response(json.dumps({'token': token.token, 'uid':uid,'code':'00'},
                sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        else:
            abort(LOGIN_INVALID, status=401)

    # API 2
    @http.route('/api/create/product', auth='none', type='json', methods=['POST'], csrf=False)
    def api_create_product(self, model='product.template', context=None, **kw):
        _logger.info(f"********* ISNIDE Product Creation Data *****: {request}.")
        data = json.loads(request.httprequest.data)
        values={}
        _logger.info(f"********* ISNIDE Product Creation Data *****: {data}.")
        token = data.get('TOKEN')
        default_code = data.get('ONLITM')
        barcode = data.get('ONITM')
        description = data.get('ONDSC2')
        type = "product"
        available_in_pos = True
        list_price = data.get('ONUPRC')
        name = data.get('ONDSC1')
        uom = data.get('ONUOM')
        qty = data.get("ONPQOH")
        effect_date = data.get("ONEFTJ")
        expiry_date = data.get("ONEXDJ")

        check_params({'token': token,
                      'default_code': default_code,
                      'barcode': barcode,
                      'description': description,
                      'list_price': list_price,
                      'name': name,
                      'uom': uom,
                      'qty': qty,
                      'effect_date': effect_date,
                      'expiry_date': expiry_date,
                      })
                      
        _logger.info(f"********* entity_data *****: {check_params}.")
        ensure_db()
        token_valid = check_token_trans(token)
        _logger.info(f"********* token_valid *****: {token_valid}.")        
        if not token_valid:
            error = {"error": "token_invalid","code":"01"}
            return error
        else:
            try: 
                UOM = request.env['uom.uom'].search([('name', '=', str(uom))])
                if UOM:
                    uom_id = UOM
                else:
                    uom_id = request.env['uom.uom'].create({'name': str(uom),'active':True,'category_id':1,'type':'reference','rounding':1.0 })
                _logger.info(f"********* UOM ID *****: {uom_id.id}.")
                name = str(name).title()
                _logger.info(f"********* PRODUCt NAME *****: {name}.")
                product_id = request.env[model].search([('default_code', '=',str(default_code)),('name', '=', name)])
                _logger.info(f"********* PRODUCt ID *****: {product_id}.")
                if product_id:
                    result = {"product_id": product_id.id,"name": product_id.name,"msg": "Product alredy exist in ERP","code":"01","status":"400"}
                    return result
                values['name'] = name
                values['uom_id'] = uom_id.id
                values['uom_po_id'] = uom_id.id                
                values['default_code'] = default_code
                values['barcode'] = barcode
                values['description'] = description
                values['type'] = 'product'
                values['available_in_pos'] = True
                values['list_price'] = list_price
                
                product_id = request.env[model].create(values)
                _logger.info(f"********* PRODUCt Result *****: {product_id}.")
                if effect_date and expiry_date:
                    effect_date = datetime.strptime(effect_date, '%Y-%m-%d %H:%M:%S')
                    expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d %H:%M:%S')
                    _logger.info(f"********* PRODUCt DATE *****: {effect_date}.")
                    date_id = request.env['product.date.mapping'].create({'product_tmp_id': product_id.id,'effect_date':effect_date,'expiry_date':expiry_date,'status':True})
                    _logger.info(f"********* PRODUCt DATE *****: {date_id}.")

                result = {"product_id": product_id.id,"name": product_id.name,"msg": "'Product successfully created in ERP","code":"00","status":"200"}
                return result

            except Exception as error:
                _logger.error(error)
                abort({'error': traceback.format_exc(),'code':'01'}, rollback=True, status=400)



    #API 3
    @http.route('/api/create/inventory', auth='none', type='json', methods=['POST'], csrf=False)
    def api_create(self, model='stock.picking', context=None, **kw):
        data = json.loads(request.httprequest.data)
        values={}
        product_lst = []
        _logger.info(f"********* ISNIDE Product Creation Data *****: {data}.")
        token = data.get('TOKEN')
        inv_number = data.get('DOC') #Document Number
        inv_type = data.get('DCT') #Document Type
        date = data.get('TRDJ')
        items = data.get('ITEMS')       
        check_params({'token': token,
                      'inv_number': inv_number,
                      'inv_type': inv_type,
                      'date': date,
                      'items': items,
                      })
                      
        _logger.info(f"********* entity_data *****: {check_params}.")
        ensure_db()
        token_valid = check_token_trans(token)
        _logger.info(f"********* token_valid *****: {token_valid}.")        
        if not token_valid:
            error = {"error": "token_invalid","code":"01"}
            return error
        else:
            try:
                _logger.info(f"********* ITEMS *****: {items}.")
                if items:
                    for products in items:
                        _logger.info(f"********* PRODUCt DICT *****: {products}.")
                        product_id = request.env['product.product'].search([('product_tmpl_id', '=',products['PRODUCTID'])])
                        _logger.info(f"********* PRODUCT ID *****: {product_id.id}.")
                        if not product_id:
                            result = {"product_id": products['PRODUCTID'],"msg": "Product not exist in ERP. Please first create it","code":"01","status":"400"}
                            return result
                        UOM = request.env['uom.uom'].search([('name', '=', str(products['UOM']))])
                        if UOM:
                            uom_id = UOM
                        else:
                            uom_id = request.env['uom.uom'].create({'name': str(products['UOM']),'active':True,'category_id':1,'type':'reference','rounding':1.0 })
                        _logger.info(f"********* UOM ID *****: {uom_id.id}.")

                        product_lst.append((0, 0, {
                            'product_id':product_id.id,
                            'product_uom_qty':products['QTY'],
                            'quantity_done':products['QTY'],
                            'product_uom': uom_id.id, 
                            'name': product_id.name, 
                            'state': 'assigned', 
                        }))
                        
                        _logger.info('***** Product LIST %s****-----' ,product_lst)
                                                

                values['origin'] = str(inv_number) +'-'+ str(inv_type)
                values['picking_type_id'] = 1 
                values['location_id'] = 4                 
                values['location_dest_id'] = 8                 
                values['state'] = 'assigned'                
                values['scheduled_date'] = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                values['move_lines'] = product_lst                
                picking_id = request.env[model].create(values)
                _logger.info(f"********* PCKING ID *****: {picking_id}.")
                if picking_id:
                    _logger.info(f"********* picking_id id *****: {picking_id}.")
                    result = {"INVID": picking_id.id,"REF": picking_id.name,"msg": "'Inventory successfully created in ERP","code":"00","status":"200"}
                    return result
            except Exception as error:
                _logger.error(error)
                abort({'error': traceback.format_exc(),'code':'01'}, rollback=True, status=400)


    #API 4
    @http.route('/api/write/product', auth="none", type='json', methods=['POST'], csrf=False)
    def api_write(self, model='product', **kw):
        data = json.loads(request.httprequest.data)
        values={}
        _logger.info(f"********* ISNIDE Product Update Data *****: {data}.")
        token = data.get('TOKEN')
        default_code = data.get('ONLITM')
        product_id = data.get('PRODUCTID')
        effect_date = data.get("ONEFTJ")
        expiry_date = data.get("ONEXDJ")
        check_params({'product_id': product_id, 'token': token})                      
        _logger.info(f"********* entity_data *****: {check_params}.")
        ensure_db()
        token_valid = check_token_trans(token)
        _logger.info(f"********* token_valid *****: {token_valid}.")        
        if not token_valid:
            error = {"error": "token_invalid","code":"01"}
            return error
        else:
            try:
                records = request.env['product.template'].search([['id', '=', product_id]], limit=1)
                if records:
                    date_id = request.env['product.date.mapping'].create({'product_tmp_id': product_id,'effect_date':effect_date,'expiry_date':expiry_date,'status':True})
                    result = {"product_id": product_id,"name": records.name,"effect_date":str(effect_date),"expiry_date":str(expiry_date),"msg": "Product Dates updated in ERP","code":"01","status":"200",'update_flag':True}
                    return result

            except Exception as error:
                _logger.error(error)
                abort({'error': traceback.format_exc()}, rollback=True, status=400)
                     
