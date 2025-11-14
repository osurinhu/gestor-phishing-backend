from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, current_user
from flask import make_response
from service.template_service import TemplateService
from . import StrLen, page_args

ns = Namespace('Template', 'Target crud operations', path='/template')

template_creation_args = reqparse.RequestParser()
template_creation_args.add_argument('name', type=StrLen(50), help='The name of the template being created', location='form', required=True)
template_creation_args.add_argument('desc', type=StrLen(lenght=200, min=0), help='The description of the template being created', location='form')
template_creation_args.add_argument('code', type=str, help='The html code of the template being created', location='form', required=True)

template_put_args = template_creation_args.copy()
template_put_args.add_argument('id', type=int, help='The id of the template', location='args', required=True)

template_query_args = page_args.copy()
template_query_args.add_argument('id', type=str, help='The id of the template', location='args', default='')
template_query_args.add_argument('name', type=str, help='The name of the template', location='args', default='')

@ns.route('/')
class Template(Resource):
    @jwt_required()
    @ns.doc(security='bearerAuth')
    @ns.expect(template_query_args)
    def get(self):
        args = template_query_args.parse_args(strict=True)

        page = TemplateService(current_user.id).get_page_filtered(
            page=args['page'], per_page=args['per_page'],
            id=args['id'],
            name=args['name'])
        return make_response(page, 200)

    @jwt_required()
    @ns.doc(security='bearerAuth')
    @ns.expect(template_creation_args)
    def post(self):
        args = template_creation_args.parse_args(strict=True)
        try:
            template =  TemplateService(current_user.id).create(
                name=args['name'],
                description=args['desc'],
                code=args['code']
            )
            return make_response(template, 201)
        except:
            abort(500, message='Coudnt create template', error='Internal Error')

    @jwt_required()
    @ns.doc(security='bearerAuth')
    @ns.expect(template_put_args)
    def put(self):
        args = template_put_args.parse_args(strict=True)
        try:
            template =  TemplateService(current_user.id).put(
                id=args['id'],
                name=args['name'],
                description=args['desc'],
                code=args['code']
            )
            return make_response(template, 200)
        except:
            abort(500, message='Coudnt create template', error='Internal Error')

@ns.route('/<int:id>')
class TemplateId(Resource):
    @jwt_required()
    @ns.doc(security='bearerAuth')
    def get(self, id):
        try:
            group = TemplateService(current_user.id).get_by_id(id=id, extra_fields=('code',))
            if not group:
                raise PermissionError
            return make_response(group, 200)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except:
            return abort(500, message='Coudnt get template', error='Internal Error')
    
    @jwt_required()
    @ns.doc(security='bearerAuth')
    def delete(self, id):
        try:
            group = TemplateService(current_user.id).delete(id)
            return make_response(group, 200)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except RuntimeError:
            return abort(400, message='Template cant be deleted', error={'template':'Template has a campaign active right now'})
        except:
            return abort(500, message='Coudnt delete template', error='Internal Error')

