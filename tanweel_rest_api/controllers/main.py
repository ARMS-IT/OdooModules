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
        module = env['ir.module.module'].search([['name', '=', "tanweel_rest_api"]], limit=1)
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

    # def default(self, obj):
    #     print("+++++++++++",obj)
    #     def encode(item):
    #         if isinstance(item, models.BaseModel):
    #             vals = {}
    #             for name, field in item._fields.items():
    #                 if name in item:
    #                     if isinstance(item[name], models.BaseModel):
    #                         records = item[name]
    #                         if len(records) == 1:
    #                             # try:
    #                             #     vals[name] = (records.id, records.sudo().display_name, records.sudo().state, records.sudo().lat, records.sudo().lng, records.sudo().flexibility)
    #                             # except:
    #                             #     vals[name] = (records.id, records.sudo().display_name)
    #                             val = []
    #                             for record in records:
    #                                 try:
    #                                     val.append((record.id, record.sudo().display_name, record.sudo().state, record.sudo().lat, record.sudo().lng, record.sudo().flexibility, record.sudo().description))
    #                                 except:
    #                                     val.append((record.id, record.sudo().display_name))
    #                             vals[name] = val
    #                         else:
    #                             val = []
    #                             for record in records:
    #                                 try:
    #                                     val.append((record.id, record.sudo().display_name, record.sudo().state, record.sudo().lat, record.sudo().lng, record.sudo().flexibility, record.sudo().description))
    #                                 except:
    #                                     val.append((record.id, record.sudo().display_name))
    #                             vals[name] = val
    #                     else:
    #                         try:
    #                             vals[name] = item[name].decode()
    #                         except UnicodeDecodeError:
    #                             vals[name] = item[name].decode('latin-1')
    #                         except AttributeError:
    #                             vals[name] = item[name]
    #                 else:
    #                     vals[name] = None
    #             return vals
    #         if inspect.isclass(item):
    #             return item.__dict__
    #         try:
    #             return json.JSONEncoder.default(self, item)
    #         except TypeError:
    #             return "error"
    #     try:
    #         try:
    #             result = {}
    #             for key, value in obj.items():
    #                 result[key] = encode(item)
    #             return result
    #         except AttributeError:
    #             result = []
    #             for item in obj:
    #                 result.append(encode(item))
    #             return result
    #     except TypeError:
    #         return encode(item)

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
    
    @http.route('/api/change_master_password', auth="none", type='http', methods=['POST'], csrf=False)
    def api_change_password(self, password_old="admin", password_new=None, **kw):
        check_params({'password_new': password_new})
        try:
            http.dispatch_rpc('db', 'change_admin_password', [
                password_old,
                password_new])
            return Response(json.dumps(True,
                sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    @http.route('/api/database/list', auth="none", type='http', csrf=False)
    def api_database_list(self, **kw):
        databases = []
        incompatible_databases = []
        try:
            databases = http.db_list()
            incompatible_databases = odoo.service.db.list_db_incompatible(databases)
        except odoo.exceptions.AccessDenied:
            monodb = http.db_monodb()
            if monodb:
                databases = [monodb]
        info = {
            'databases': databases,
            'incompatible_databases': incompatible_databases}
        return Response(json.dumps(info,
            sort_keys=True, indent=4, cls=ObjectEncoder),
            content_type='application/json;charset=utf-8', status=200)

    @http.route('/api/database/create', auth="none", type='http', methods=['POST'], csrf=False)
    def api_database_create(self, master_password="admin", lang="en_US", database_name=None, 
                        admin_login=None, admin_password=None, **kw):
        check_params({
            'database_name': database_name,
            'admin_login': admin_login,
            'admin_password': admin_password})
        try:
            if not re.match(DBNAME_PATTERN, database_name):
                raise Exception(_('Invalid database name.'))
            http.dispatch_rpc('db', 'create_database', [
                master_password,
                database_name,
                bool(kw.get('demo')),
                lang,
                admin_password,
                admin_login,
                kw.get('country_code') or False])
            return Response(json.dumps(True,
                sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)
    
    @http.route('/api/database/duplicate', auth="none", type='http', methods=['POST'], csrf=False)
    def api_database_duplicate(self, master_password="admin", database_old=None, database_new=None, **kw):
        check_params({
            'database_old': database_old,
            'database_new': database_new})
        try:
            if not re.match(DBNAME_PATTERN, database_new):
                raise Exception(_('Invalid database name.'))
            http.dispatch_rpc('db', 'duplicate_database', [
                master_password,
                database_old,
                database_new])
            return Response(json.dumps(True,
                sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)
    
    @http.route('/api/database/drop', auth="none", type='http', methods=['POST'], csrf=False)
    def api_database_drop(self, master_password="admin", database_name=None, **kw):
        check_params({'database_name': database_name})
        try:
            http.dispatch_rpc('db','drop', [
                master_password,
                database_name])
            request._cr = None
            return Response(json.dumps(True,
                sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)

    #----------------------------------------------------------
    # Backup & Restore
    #----------------------------------------------------------        
    
    @http.route('/api/database/backup', auth="none", type='http', methods=['POST'], csrf=False)
    def api_database_backup(self, master_password="admin", database_name=None, backup_format='zip', **kw):
        check_params({'database_name': database_name})
        try:
            odoo.service.db.check_super(master_password)
            ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            filename = "%s_%s.%s" % (database_name, ts, backup_format)
            headers = [
                ('Content-Type', 'application/octet-stream; charset=binary'),
                ('Content-Disposition', http.content_disposition(filename)),
            ]
            dump_stream = odoo.service.db.dump_db(database_name, None, backup_format)
            return Response(dump_stream, headers=headers, direct_passthrough=True)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)
            
    @http.route('/api/database/restore', auth="none", type='http', methods=['POST'], csrf=False)
    def api_restore(self, master_password="admin", backup_file=None, database_name=None, copy=False, **kw):
        check_params({'backup_file': backup_file, 'database_name': database_name})
        try:
            with tempfile.NamedTemporaryFile(delete=False) as data_file:
                backup_file.save(data_file)
            odoo.service.db.restore_db(database_name, data_file.name, str2bool(copy))
            return Response(json.dumps(True,
                sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, status=400)
        finally:
            os.unlink(data_file.name)

    @http.route('/api/refresh', auth="none", type='http', methods=['POST'], csrf=False)
    def api_refresh(self, token=None, **kw):
        check_params({'token': token})
        ensure_db()
        check_token()
        env = api.Environment(request.cr, odoo.SUPERUSER_ID, {})
        result = env['rest.api.token'].refresh_token(token)
        return Response(json.dumps(result,
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
    # System
    #----------------------------------------------------------
        
    @http.route([
        '/api/search',
        '/api/search/<string:model>',
        '/api/search/<string:model>/<int:id>',
        '/api/search/<string:model>/<int:id>/<int:limit>',
        '/api/search/<string:model>/<int:id>/<int:limit>/<int:offset>'], auth="none", type='http', csrf=False)
    def api_search(self, model='res.partner', id=None, domain=None, context=None, count=False,
               limit=80, offset=0, order=None, token=None, **kw):
        check_params({'token': token})
        ensure_db()
        check_token()
        try:
            args = domain and json.loads(domain) or []
            if id:
                args.append(['id', '=', id])
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            count = count and bool(count) or None
            limit = limit and int(limit) or None
            offset = offset and int(offset) or None
            model = request.env[model].with_context(default)
            result = model.sudo().search(args, offset=offset, limit=limit, order=order, count=count)
            return Response(json.dumps(result,
                sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)
        
    @http.route([
        '/api/read',
        '/api/read/<string:model>',
        '/api/read/<string:model>/<int:id>',
        '/api/read/<string:model>/<int:id>/<int:limit>',
        '/api/read/<string:model>/<int:id>/<int:limit>/<int:offset>'], auth="none", type='http', csrf=False)
    def api_read(self, model='res.partner', id=None, fields=None, domain=None, context=None,
             limit=80, offset=0, order=None, token=None, **kw):
        check_params({'token': token})
        ensure_db()
        check_token()
        try:
            fields = fields and json.loads(fields) or None
            args = domain and json.loads(domain) or []
            if id:
                args.append(['id', '=', id])
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            limit = limit and int(limit) or None
            offset = offset and int(offset) or None
            model = request.env[model].with_context(default)
            result = model.search_read(domain=args, fields=fields, offset=offset, limit=limit, order=order)
            return Response(json.dumps(result,
                sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)
            
    # @http.route('/api/create', auth="none", type='http', methods=['POST'], csrf=False)
    # def api_create(self, model='res.partner', values=None, context=None, token=None, **kw):
    #     check_params({'token': token})
    #     ensure_db()
    #     check_token()
    #     try:
    #         values = values and json.loads(values) or {}
    #         context = context and json.loads(context) or {}
    #         default = request.session.context.copy()
    #         default.update(context)
    #         model = request.env[model].with_context(default)
    #         result = model.create(values)
    #         return Response(json.dumps(result,
    #             sort_keys=True, indent=4, cls=ObjectEncoder),
    #             content_type='application/json;charset=utf-8', status=200)
    #     except Exception as error:
    #         _logger.error(error)
    #         abort({'error': traceback.format_exc()}, rollback=True, status=400)

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

    #tanweel API 2
    @http.route('/api/create/partner', auth='none', type='http', methods=['POST'], csrf=False)
    def api_create(self, model='res.partner',values=None, context=None, token=None, **kw):
        check_params({'token': token,'values':values,
                      'customer_ref': json.loads(values).get('ref'),
                      'customer_name': json.loads(values).get('name'),})
        ensure_db()
        check_token()
        try:
            values = values and json.loads(values) or {}
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            name = str(values.get('name')).title()
            model = request.env[model].with_context(default)
            partner_id = model.search([('ref', '=',str(values.get('ref'))),('name', '=', name)])
            if partner_id:
                return Response(json.dumps({'name': partner_id[0].name,'id': partner_id[0].id,'code': '01',
                                            'msg': 'Customer alredy exist in ERP.'},
                sort_keys=True, indent=4,cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=400)
            values['name'] = name
            result = model.create(values)
            return Response(json.dumps({'name': result.name,'id': result.id,'code': '00','msg': 'Customer successfully created in ERP.'},
                sort_keys=True, indent=4,cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc(),'code':'01'}, rollback=True, status=400)

    #tanweel API 3
    @http.route('/api/create/transaction', type='json', auth='none', methods=["POST"], csrf=False)
    def api_transaction(self, model='account.move', **kwargs):
        data = json.loads(request.httprequest.data)
        token = data.get('token')
        pay_txn_id = data.get('pay_txn_id')
        cus_id = data.get('cus_id')
        cus_name = data.get('cus_name')
        app_id = data.get('app_id')
        prod_code = data.get('prod_code')
        prod_name = data.get('prod_name')
        pay_amount = data.get('pay_amount')
        loan_type_code = data.get('loan_type_code')
        pay_txn_datetime = data.get('pay_txn_datetime')
        pay_session_id = data.get('pay_session_id')

        param_dict = check_params_trans({'token': token,
                      'pay_txn_id': pay_txn_id,
                      'cus_id': cus_id,
                      'cus_name': cus_name,
                      'app_id': app_id,
                      'prod_code': prod_code,
                      'prod_name': prod_name,
                      'pay_amount': pay_amount,
                      'loan_type_code': loan_type_code,
                      'pay_txn_datetime': pay_txn_datetime,
                      'pay_session_id': pay_session_id,
                      })
        if not param_dict.get('param_valid'):
            # abort({'error': traceback.format_exc(),'code':'01'}, rollback=True, status=400)
            return param_dict
        ensure_db()
        token_valid = check_token_trans(token)
        if not token_valid:
            error = {
                "error": "token_invalid",
                "code":"01"
            }
            return error
        else:
            try:
                from datetime import datetime
                import pytz
                cus_name = str(cus_name).title()
                Partner = request.env['res.partner']
                partner_id = Partner.search([('id', '=', cus_id),('name', '=', cus_name)])
                if partner_id:
                    partner_id = partner_id[0]
                else:
                    partner_id = Partner.create({'name': cus_name})
                Product = request.env['product.product']
                prod_name = str(prod_name).title()
                product_id = Product.search([('default_code', '=', prod_code),('name', '=', prod_name)])
                if product_id:
                    product_id = product_id[0]
                else:
                    product_id = Product.create({'name': prod_name,'default_code': prod_code})

                pay_txn_datetime = datetime.strptime(pay_txn_datetime, '%Y-%m-%d %H:%M:%S')
                move_vals = {
                    'ref': partner_id.ref,
                    'move_type': 'out_invoice',
                    'initial_amount': pay_amount,
                    'partner_id': partner_id.id,
                    'pay_txn_id': pay_txn_id,
                    'loan_type_code': loan_type_code,
                    'pay_txn_datetime': fields.Datetime.to_string(pay_txn_datetime - timedelta(hours=5,minutes=30)),
                    'pay_session_id': pay_session_id,
                    'app_id': app_id,
                    'invoice_line_ids': [(0, 0, {
                        'price_unit': pay_amount,
                        'quantity': 1.0,
                        'product_id': product_id.id,
                    })],
                }
                move = request.env[model].create(move_vals)
                result = {"cus_id": partner_id.id,"erp_txn_id": move.id,"msg": "As generated in ERP system when payment transaction is noted and logged in ERP system.","code":"00","status":"200"}
                # return Response(json.dumps({'cus_id': partner_id.id,'erp_txn_id': move.id,"msg":"As generated in ERP system when payment transaction is noted and logged in ERP system.",'code':'00'},
                #     sort_keys=True, indent=4,cls=ObjectEncoder),
                #     content_type='application/json', status=200)
                return result
            except Exception as error:
                _logger.error(error)
                result = {"error": traceback.format_exc(),"code":"01","status":"400"}
                # abort({'error': traceback.format_exc(),'code':'01'}, rollback=True, status=400)
                return result

    # #tanweel API 3
    # # @http.route('/api/create/transaction', auth="none", type='http', methods=['POST'], csrf=False)
    # @http.route('/api/create/transaction', auth="none", type='json', methods=['POST'], csrf=False)
    # def api_transaction(self, model='account.move',
    #                     pay_txn_id=None,data={},
    #                     cus_id=None, cus_name=None, product_values={},
    #                     prod_code=None, prod_name=None, app_id=None,
    #                     pay_amount=None, loan_type_code=None, pay_txn_datetime=None,
    #                     pay_session_id=None, context=None, token=None, **kw):
    #     print("===****kw********====",kw)
    #     print("===*******cus_id*****====",cus_id)
    #     print("===*******json*****====",json.loads(data))
    #     # print("===********pay****====",json.loads(pay_txn_id))
    #     # print("===pay_txn_id====",pay_txn_id,type(pay_txn_id))
    #
    #     params =    { 'token': token,
    #                   'pay_txn_id': pay_txn_id,
    #                   # 'customer_values': customer_values,
    #                   'cus_id': cus_id,
    #                   'cus_name': cus_name,
    #                   # 'cus_name': json.loads(customer_values).get('name'),
    #                   'app_id': app_id,
    #                   # 'product_values': product_values,
    #                   # 'default_code': json.loads(product_values).get('default_code'),
    #                   'prod_code': prod_code,
    #                   'prod_name': prod_name,
    #                   'pay_amount': pay_amount,
    #                   'loan_type_code': loan_type_code,
    #                   'pay_txn_datetime': pay_txn_datetime,
    #                   'pay_session_id': pay_session_id,
    #                   }
    #
    #     print("params...",params)
    #
    #     check_params({'token': token,
    #                   'pay_txn_id': pay_txn_id,
    #                   # 'customer_values': customer_values,
    #                   'cus_id': cus_id,
    #                   'cus_name': cus_name,
    #                   # 'cus_name': json.loads(customer_values).get('name'),
    #                   'app_id': app_id,
    #                   # 'product_values': product_values,
    #                   # 'default_code': json.loads(product_values).get('default_code'),
    #                   'prod_code': prod_code,
    #                   'prod_name': prod_name,
    #                   'pay_amount': pay_amount,
    #                   'loan_type_code': loan_type_code,
    #                   'pay_txn_datetime': pay_txn_datetime,
    #                   'pay_session_id': pay_session_id,
    #                   })
    #     ensure_db()
    #     check_token()
    #     try:
    #         pay_txn_id = pay_txn_id and json.loads(pay_txn_id) or ''
    #         # customer_values = customer_values and json.loads(customer_values) or {}
    #         cus_id = cus_id and json.loads(cus_id) or ''
    #         cus_name = cus_name and json.loads(cus_name) or ''
    #         app_id = app_id and json.loads(app_id) or ''
    #         prod_code = prod_code and json.loads(prod_code) or ''
    #         prod_name = prod_name and json.loads(prod_name) or ''
    #         # product_values = product_values and json.loads(product_values) or ''
    #         pay_amount = pay_amount and json.loads(pay_amount) or 0.0
    #         loan_type_code = loan_type_code and json.loads(loan_type_code) or ''
    #         pay_txn_datetime = pay_txn_datetime and json.loads(pay_txn_datetime) or ''
    #         pay_session_id = pay_session_id and json.loads(pay_session_id) or ''
    #
    #         from datetime import datetime
    #         import pytz
    #
    #         # pay_txn_datetime = datetime.strptime(pay_txn_datetime, '%Y-%m-%d %H:%M:%S')
    #         # local = pytz.timezone(request.env.user.tz or pytz.utc)
    #         # print("local...",local)
    #         # pay_txn_datetime = datetime.strftime(pytz.utc.localize(pay_txn_datetime).astimezone(local),"%Y-%m-%d %H:%M:%S")
    #         # print("pay_txn_datetime....",pay_txn_datetime)
    #
    #         # customer_name = str(customer_values.get('name')).title()
    #         cus_name = str(cus_name).title()
    #         Partner = request.env['res.partner']
    #         # partner_id = Partner.search([('id', '=', customer_values.get('cus_id')),('name', '=', customer_name)])
    #         partner_id = Partner.search([('id', '=', cus_id),('name', '=', cus_name)])
    #         if partner_id:
    #             partner_id = partner_id[0]
    #         else:
    #             partner_id = Partner.create({'name': cus_name})
    #         Product = request.env['product.product']
    #         # product_id = Product.search([('default_code', '=', product_values.get('default_code')),('name', '=', str(product_values.get('name')).title())])
    #         prod_name = str(prod_name).title()
    #         product_id = Product.search([('default_code', '=', prod_code),('name', '=', prod_name)])
    #         if product_id:
    #             product_id = product_id[0]
    #         else:
    #             product_id = Product.create({'name': prod_name,'default_code': prod_code})
    #
    #         pay_txn_datetime = datetime.strptime(pay_txn_datetime, '%Y-%m-%d %H:%M:%S')
    #
    #         move_vals = {
    #             'ref': partner_id.ref,
    #             'move_type': 'out_invoice',
    #             'initial_amount': pay_amount,
    #             # 'invoice_origin': order.name,
    #             # 'invoice_user_id': order.user_id.id,
    #             # 'narration': order.note,
    #             'partner_id': partner_id.id,
    #             'pay_txn_id': pay_txn_id,
    #             'loan_type_code': loan_type_code,
    #             'pay_txn_datetime': fields.Datetime.to_string(pay_txn_datetime - timedelta(hours=5,minutes=30)),
    #             'pay_session_id': pay_session_id,
    #             'app_id': app_id,
    #             # 'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
    #             # 'partner_shipping_id': order.partner_shipping_id.id,
    #             # 'currency_id': order.pricelist_id.currency_id.id,
    #             # 'payment_reference': order.reference,
    #             # 'invoice_payment_term_id': order.payment_term_id.id,
    #             # 'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
    #             # 'team_id': order.team_id.id,
    #             # 'campaign_id': order.campaign_id.id,
    #             # 'medium_id': order.medium_id.id,
    #             # 'source_id': order.source_id.id,
    #             'invoice_line_ids': [(0, 0, {
    #                 # 'name': name,
    #                 'price_unit': pay_amount,
    #                 'quantity': 1.0,
    #                 'product_id': product_id.id,
    #                 # 'product_uom_id': so_line.product_uom.id,
    #                 # 'tax_ids': [(6, 0, so_line.tax_id.ids)],
    #                 # 'sale_line_ids': [(6, 0, [so_line.id])],
    #                 # 'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
    #                 # 'analytic_account_id': order.analytic_account_id.id or False,
    #             })],
    #         }
    #
    #         move = request.env[model].create(move_vals)
    #         # move.action_post()
    #         # return Response(json.dumps({'erp_txn_number': move.name,'erp_txn_id': move.id,"msg":"As generated in ERP system when payment transaction is noted and logged in ERP system.",'code':'00'},
    #         return Response(json.dumps({'cus_id': partner_id.id,'erp_txn_id': move.id,"msg":"As generated in ERP system when payment transaction is noted and logged in ERP system.",'code':'00'},
    #             sort_keys=True, indent=4,cls=ObjectEncoder),
    #             content_type='application/json;charset=utf-8', status=200)
    #     except Exception as error:
    #         _logger.error(error)
    #         abort({'error': traceback.format_exc(),'code':'01'}, rollback=True, status=400)

    #tanweel API 4
    @http.route('/api/closeloan', auth='none', type='http', methods=['POST'], csrf=False)
    def api_close_loan(self, model='account.move',
                        erp_txn_id = None,
                        loan_amount=None,fe_id=None,
                        context=None, token=None, **kw):
        check_params({'token': token,
                      'erp_txn_id': erp_txn_id,
                      # 'pay_txn_id': pay_txn_id,
                      'loan_amount': loan_amount,
                      'fe_id': fe_id,
                      })
        ensure_db()
        check_token()
        try:
            erp_txn_id = erp_txn_id and json.loads(erp_txn_id) or ''
            # pay_txn_id = pay_txn_id and json.loads(pay_txn_id) or ''
            loan_amount = loan_amount and json.loads(loan_amount) or 0.0
            fe_id = fe_id and json.loads(fe_id) or ''
            move_rec = request.env[model].search([('id', '=', int(erp_txn_id))])
            if not move_rec:
                return Response(json.dumps({'erp_txn_id': erp_txn_id,'code': '01',
                                            'msg': 'This transaction Id not found in ERP.'},
                sort_keys=True, indent=4,cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=400)
            # if move_rec.state != 'posted':
            #     return Response(json.dumps({'erp_txn_id': erp_txn_id,'pay_txn_id': pay_txn_id,'code': '01',
            #                                 'msg': 'This transaction Id not in posted state.'},
            #     sort_keys=True, indent=4,cls=ObjectEncoder),
            #     content_type='application/json;charset=utf-8', status=400)

            company_id = move_rec.company_id
            domain = [
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', company_id.id),
            ]
            journal = request.env['account.journal'].search(domain, limit=1)
            amount = float(loan_amount)
            communication = move_rec.name

            available_payment_methods = journal.inbound_payment_method_ids
            # move_rec.button_draft()
            move_rec.fe_id = fe_id

            # current_invoice_lines = move_rec.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)
            # for line in current_invoice_lines:
            #     price_subtotal = line._get_price_total_and_subtotal().get('price_subtotal', 0.0)
            #     to_write = line._get_fields_onchange_balance(price_subtotal=price_subtotal)
            #     to_write.update(line._get_price_total_and_subtotal(
            #         price_unit=to_write.get('price_unit', amount),
            #     ))

            # current_invoice_lines.price_unit = amount
            # others_lines = move_rec.line_ids - current_invoice_lines
            # if others_lines and current_invoice_lines - move_rec.invoice_line_ids:
            #     others_lines[0].recompute_tax_line = True
            # move_rec.line_ids = others_lines + move_rec.invoice_line_ids
            # move_rec._onchange_recompute_dynamic_lines()


            # for line in move_rec.invoice_line_ids:
            #     print("%%%%%%%%%",line.exclude_from_invoice_tab)
            #     move_rec._onchange_invoice_line_ids()
            #     move_rec.line_ids._onchange_price_subtotal()
            #     move_rec._recompute_dynamic_lines(recompute_all_taxes=True)
            #     line._get_computed_price_unit()
            #     line.sudo().price_unit = amount

            # move_rec.action_post()
            # for line in move_rec.invoice_line_ids:
            #     print("&&&&&&&&&",line.price_unit)

            # 'amount': 800.0,
            # 'group_payment': True,
            # 'payment_difference_handling': 'reconcile',
            # 'writeoff_account_id': self.company_data['default_account_revenue'].id,
            # 'writeoff_label': 'writeoff',
            # 'payment_method_id': self.custom_payment_method_in.id,

            # for line in move_rec:
            #     cleaned_vals = line.move_id._cleanup_write_orm_values(line, {'price_unit':amount})
            #     if not cleaned_vals:
            #         continue
            #
            # ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
            # for line in move_rec.invoice_line_ids:
            #     price_subtotal = line._get_price_total_and_subtotal().get('price_subtotal', 0.0)
            #     to_write = line._get_fields_onchange_balance(price_subtotal=price_subtotal)
            #     to_write.update(line._get_price_total_and_subtotal(
            #         price_unit=to_write.get('price_unit',amount),
            #     ))
            # print("&&&&&&&&&",line.price_unit)
            # line.price_unit = amount
            # line._onchange_price_subtotal()
            # line._compute_balance()
            # line._compute_cumulated_balance()

            # for line in move_rec.line_ids:
            #     print("====line.price_unit======",line.price_unit)
            #     line.write({'price_unit':amount,'debit':amount,'credit':amount})
            #     print("====line.price_unit======",line.price_unit)
            #
            #
            # for line in move_rec.invoice_line_ids:
            #     print("====line.price_unit======",line.price_unit)
            #     line.write({'price_unit':amount,'debit':amount,'credit':amount})
            #     print("====line.price_unit======",line.price_unit)
            # We use account_predictive_bills_disable_prediction context key so that
            # this doesn't trigger prediction in case enterprise (hence account_predictive_bills) is installed

            for line in move_rec.invoice_line_ids:
                line.with_context(check_move_validity=False).write({'price_unit':amount})
            move_rec.with_context(check_move_validity=False)._recompute_dynamic_lines()
            move_rec.action_post()
            payments = request.env['account.payment.register'].with_context(active_model='account.move', active_ids=move_rec.id).create({
                'amount': amount,
                # 'group_payment': True,
                # 'payment_difference_handling': 'open',
                'payment_method_id': available_payment_methods[0].id,
                 })._create_payments()
            # payment_register_id = models.execute_kw(db, uid, password, 'account.payment.register', 'create', [{'journal_id': bank_journal_id, 'payment_method_id': payment_method_id, 'invoice_ids': [(4, invoice_id)]}])
            # models.execute_kw(db, uid, password, 'account.payment.register', 'create_payments', [[payment_register_id]])
            return Response(json.dumps({'payment_txn_number': payments.name,'payment_txn_id': payments.id,"msg":"Payment generated in ERP with updated amount.",'code':'00'},
                sort_keys=True, indent=4,cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc(),'code':'01'}, rollback=True, status=400)

    #tanweel API 5
    @http.route('/api/refund', auth='user', type='http', methods=['POST'], csrf=False)
    def api_refund(self, model='account.move',
                        erp_txn_id = None,
                        loan_amount=None,fe_id=None,
                        context=None, token=None, **kw):
        check_params({'token': token,
                      'erp_txn_id': erp_txn_id,
                      # 'pay_txn_id': pay_txn_id,
                      # 'loan_amount': loan_amount,
                      })
        ensure_db()
        check_token()
        try:
            erp_txn_id = erp_txn_id and json.loads(erp_txn_id) or ''
            # pay_txn_id = pay_txn_id and json.loads(pay_txn_id) or ''
            loan_amount = loan_amount and json.loads(loan_amount) or 0.0
            move_rec = request.env[model].search([('id', '=', int(erp_txn_id))])
            if not move_rec:
                return Response(json.dumps({'erp_txn_id': erp_txn_id,'code': '01',
                                            'msg': 'This transaction Id not found in ERP.'},
                sort_keys=True, indent=4,cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=400)
            move_ids = request.env['account.move'].browse(move_rec.id)
            refund_method = (len(move_ids) > 1 or move_ids.move_type == 'entry') and 'cancel' or 'refund'
            move_ids = [(6, 0, move_ids.ids)]
            credit_note_wizard = request.env['account.move.reversal'].with_context(active_model='account.move', active_ids=move_rec.id).create({
               'refund_method': refund_method,
               'move_ids': move_ids
            })
            invoice_refund = request.env['account.move'].browse(credit_note_wizard.reverse_moves()['res_id'])
            invoice_refund.action_post()
            company_id = move_rec.company_id
            domain = [
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', company_id.id),
            ]
            journal = request.env['account.journal'].search(domain, limit=1)
            available_payment_methods = journal.inbound_payment_method_ids
            payments = request.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice_refund.id).create({
                # 'amount': amount,
                'payment_method_id': available_payment_methods[0].id,
                 })._create_payments()
            return Response(json.dumps({'credit_note_number': invoice_refund.name,'payment_txn_id': invoice_refund.id,"msg":"Credit note created in ERP.",'code':'00'},
                sort_keys=True, indent=4,cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc(),'code':'01'}, rollback=True, status=400)

    @http.route('/api/write', auth="none", type='http', methods=['POST'], csrf=False)
    def api_write(self, model='res.partner', ids=None, values=None, context=None, token=None, **kw):
        check_params({'ids': ids, 'token': token})
        ensure_db()
        check_token()
        try:
            ids = ids and json.loads(ids) or []
            values = values and json.loads(values) or {}
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            model = request.env[model].with_context(default)
            records = model.browse(ids)
            if kw.get('location') == 'true':
                result = records.sudo().write(values)
            else:
                result = records.write(values)
            return Response(json.dumps(result,
                sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    @http.route('/api/unlink', auth="none", type='http', methods=['DELETE'], csrf=False)
    def api_unlink(self, model='res.partner', ids=None, context=None, token=None, **kw):
        check_params({'ids': ids, 'token': token})
        ensure_db()
        check_token()
        try:
            ids = ids and json.loads(ids) or []
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            model = request.env[model].with_context(default)
            records = model.browse(ids)
            result = records.unlink()
            return Response(json.dumps(result,
                sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)
            
    @http.route('/api/call', auth="none", type='http', methods=['POST'], csrf=False)
    def api_call(self, model='res.partner', method=None, ids=None, context=None, args=None,
               kwargs=None, token=None, **kw):
        check_params({'method': method, 'token': token})
        ensure_db()
        check_token()
        try:
            ids = ids and json.loads(ids) or []
            args = args and json.loads(args) or []
            kwargs = kwargs and json.loads(kwargs) or {}
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            model = request.env[model].with_context(default)
            records = model.browse(ids)
            result = getattr(records, method)(*args, **kwargs)
            return Response(json.dumps(result,
                sort_keys=True, indent=4, cls=ObjectEncoder),
                content_type='application/json;charset=utf-8', status=200)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)
            
    @http.route([
        '/api/report',
        '/api/report/<string:model>',
        '/api/report/<string:model>/<string:report>',
        ], auth="none", type='http', csrf=False)
    def api_report(self, model='res.partner', report=None, ids=None, type="pdf", context=None,
               args=None, kwargs=None, token=None, **kw):
        check_params({'report': report, 'ids': ids, 'token': token})
        ensure_db()
        check_token()
        try:
            ids = ids and json.loads(ids) or []
            args = args and json.loads(args) or []
            kwargs = kwargs and json.loads(kwargs) or {}
            context = context and json.loads(context) or {}
            default = request.session.context.copy()
            default.update(context)
            model = request.env[model].with_context(default)
            if type == "html":
                data = request.env.ref(report).render_qweb_html(ids)[0]
                headers = [
                    ('Content-Type', 'text/html'),
                    ('Content-Length', len(data)),
                ]
                return request.make_response(data, headers=headers)
            else:
                data = request.env.ref(report).render_qweb_pdf(ids)[0]
                headers = [
                    ('Content-Type', 'application/pdf'),
                    ('Content-Length', len(data)),
                ]
                return request.make_response(data, headers=headers)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)

    @http.route([
        '/api/binary',
        '/api/binary/<string:xmlid>',
        '/api/binary/<string:xmlid>/<string:filename>',
        '/api/binary/<int:id>',
        '/api/binary/<int:id>/<string:filename>',
        '/api/binary/<int:id>-<string:unique>',
        '/api/binary/<int:id>-<string:unique>/<string:filename>',
        '/api/binary/<string:model>/<int:id>/<string:field>',
        '/api/binary/<string:model>/<int:id>/<string:field>/<string:filename>'], auth="none", type='http', csrf=False)
    def api_binary(self, token=None, xmlid=None, model='ir.attachment', id=None, field='datas', filename=None,
               filename_field='datas_fname', unique=None, mimetype=None, **kw):
        ensure_db()
        check_token()
        try:
            status, headers, content = request.registry['ir.http'].binary_content(
                xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
                filename_field=filename_field, mimetype=mimetype, download=True)
            if status == 200:
                content_base64 = base64.b64decode(content)
                headers.append(('Content-Length', len(content_base64)))
                return request.make_response(content_base64, headers=headers)
            else:
                abort({'error': status}, status=status)
        except Exception as error:
            _logger.error(error)
            abort({'error': traceback.format_exc()}, rollback=True, status=400)
