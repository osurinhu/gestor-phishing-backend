from flask import jsonify
from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, current_user
from service.user_service import UserService
from . import StrLen

ns = Namespace('Auth', 'Auth related operations', path='/auth')

auth_args = reqparse.RequestParser()
auth_args.add_argument("name", type=StrLen(100), help="The usarname trying to log in", location='form', required=True)
auth_args.add_argument("password", type=StrLen(200), help="The password of the user trying to log in", location='form', required=True)

@ns.route('/')
class Auth(Resource):
    @jwt_required()
    @ns.doc(security='bearerAuth')
    def get(self):
        abort(500)
        return current_user.to_dict(only=('name','is_admin'))
    
    @ns.expect(auth_args, validate=True)
    def post(self):
        args = auth_args.parse_args(strict=True)

        service = UserService()
        jwt_token = service.auth_user(name=args.get('name'), password=args.get('password'));
        if not jwt_token:
            abort(401, 'User authentication failed', errors={'auth':'Username or passoword incorrect'})
        return jsonify(access_token=jwt_token)
    