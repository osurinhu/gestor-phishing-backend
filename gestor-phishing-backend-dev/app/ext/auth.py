from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request, jwt_required
from flask import jsonify
from repository.user_repository import UserRepo


jwt = JWTManager()  

def admin_required(f):
    """Only allow admin in route\n
        Implies a jwt check"""
    @jwt_required()
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims['sub']['is_admin']:
            return f(*args, **kwargs)
        else:
            return jsonify(msg="Admins only!"), 403
    return wrapper

@jwt.user_identity_loader
def user_identity_loader(user):
    return {'id':user.id, 'is_admin':user.is_admin}

@jwt.user_lookup_loader
def user_lookup_loader(jwt_header,jwt_payload):
    repo = UserRepo()

    id = jwt_payload['sub']['id']
    return repo.get_by_id(id)


def init_app(app):
    jwt.init_app(app)

