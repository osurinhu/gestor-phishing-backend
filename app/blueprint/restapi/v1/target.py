from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, current_user
from service.target_service import TargetService
from . import StrLen, email

ns = Namespace('Target', 'Target crud operations', path='/target')

target_update_args = reqparse.RequestParser()
target_update_args.add_argument("name", type=StrLen(50), help="The name of the target being created", location="form", default='', required = False)
target_update_args.add_argument("email", type=email, help="The email of the target being created", location="form",  default='', required = False)

@ns.route('/<int:id>')
class TargetId(Resource):
    @jwt_required()
    def get(self, id):
        try:
            group = TargetService(current_user.id).get_by_id(id=id)
            if not group:
                return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
            return group
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})

    @jwt_required()
    def patch(self, id):
        args = target_update_args.parse_args(strict=True)
        try:
            group = TargetService(current_user.id).update(
                id=id,
                name=args['name'],
                email=args['email'])
            return group
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except RuntimeError:
            return abort(400, message='Target cant be added', error={'group':'Group has a campaing active right now'})
        
    @jwt_required()
    def delete(self, id):
        try:
            return TargetService(current_user.id).delete(id)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except RuntimeError:
            return abort(400, message='Target cant be deleted', error={'group':'Group has a campaing active right now'})