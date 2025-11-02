from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, current_user
from service.template_service import TemplateService
from . import StrLen, page_args

ns = Namespace('Template', 'Target crud operations', path='/template')

template_creation_args = reqparse.RequestParser()
template_creation_args.add_argument('name', type=StrLen(25), help='The name of the template being created', location='form', required=True)
template_creation_args.add_argument('desc', type=StrLen(lenght=50, min=0), help='The description of the template being created', location='form', default='')
template_creation_args.add_argument('code', type=str, help='The html code of the template being created', location='form', required=True)

template_query_args = page_args.copy()
template_query_args.add_argument('name', type=str, help='The name of the template', location='args', default='')

template_update_args = reqparse.RequestParser()
template_update_args.add_argument('name', type=StrLen(25), help='The name of the template being updated', location='form', default='')
template_update_args.add_argument('desc', type=StrLen(lenght=50, min=0), help='The description of the template being updated', location='form', default='')
template_update_args.add_argument('code', type=str, help='The html code of the template being updated', location='form', default='')

@ns.route('/')
class Template(Resource):
    @jwt_required()
    @ns.expect(template_query_args)
    def get(self):
        args = template_query_args.parse_args(strict=True)
        return TemplateService(current_user.id).get_page_filtered(page=args['page'], per_page=args['per_page'], name=args['name'])

    @jwt_required()
    @ns.expect(template_creation_args)
    def post(self):
        args = template_creation_args.parse_args(strict=True)
        try:
            return TemplateService(current_user.id).create(
                name=args['name'],
                description=args['desc'],
                code=args['code']
            )
        except:
            abort(500, message='Coudnt create template', error='Internal Error')

@ns.route('/<int:id>')
class TemplateId(Resource):
    @jwt_required()
    @ns.expect(template_update_args)
    def patch(self, id):
        args = template_update_args.parse_args(strict=True)
        
        try:
            group = TemplateService(current_user.id).update(
                id=id,
                name=args['name'],
                description=args['desc'],
                code=args['code']),
            return group
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except RuntimeError:
            return abort(400, message='Template cant be deleted', error={'template':'Template has a campaing active right now'})
    
    @jwt_required()
    def delete(self, id):
        try:
            return TemplateService(current_user.id).delete(id)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except RuntimeError:
            return abort(400, message='Template cant be deleted', error={'template':'Template has a campaing active right now'})

