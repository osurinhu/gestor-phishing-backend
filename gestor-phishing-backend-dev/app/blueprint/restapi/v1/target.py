from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, current_user
from flask import make_response
from service.target_service import TargetService
from . import StrLen, email

ns = Namespace('Target', 'Target crud operations', path='/target')

target_update_args = reqparse.RequestParser()
target_update_args.add_argument("name", type=StrLen(50), help="The name of the target being updatedd", location="form")
target_update_args.add_argument("person_code", type=StrLen(25, 1), help="The person code of the target being updated", location="form")
target_update_args.add_argument("email", type=email, help="The email of the target being updatedd", location="form")

@ns.route('/<int:id>')
class TargetId(Resource):
    @jwt_required()
    @ns.doc(security='bearerAuth')
    def get(self, id):
        try:
            target = TargetService(current_user.id).get_by_id(id=id)
            if not target:
                raise PermissionError
            return make_response(target, 200)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except:
            return abort(500, message='Coudnt get target', error='Internal Error')

    @jwt_required()
    @ns.doc(security='bearerAuth')
    def patch(self, id):
        args = target_update_args.parse_args(strict=True)
        try:
            target = TargetService(current_user.id).update(
                id=id,
                name=args['name'],
                email=args['email'],
                person_code=args['person_code'])
            return make_response(target, 200)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except RuntimeError:
            return abort(400, message='Target cant be updated', error={'Group has a campaign active right now'})
        except FileExistsError as e:
            if e.args['email']:
                return abort(400, message='Target cant be updated', error={'Email already in use in that group'})
            if e.args['cod']:
                return abort(400, message='Target cant be updated', error={'Person code already in use in that group'})
            
        except:
            return abort(500, message='Coudnt update target', error='Internal Error')
        
    @jwt_required()
    @ns.doc(security='bearerAuth')
    def delete(self, id):
        try:
            target = TargetService(current_user.id).delete(id)
            return make_response(target, 200)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except RuntimeError:
            return abort(400, message='Target cant be deleted', error={'Group has a campaign active right now'})
        except:
            return abort(500, message='Coudnt delete target', error='Internal Error')