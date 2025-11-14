from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, current_user
from flask import jsonify, make_response
from . import StrLen, target, page_args, email
from service.group_service import GroupService
from service.target_service import TargetService

ns = Namespace('Group', 'Target group crud operations', path='/group')

group_creation_args = reqparse.RequestParser()
group_creation_args.add_argument('name', type=StrLen(50), help='The name of the group being created', location='form', required=True)
group_creation_args.add_argument('desc', type=StrLen(lenght=200, min=0), help='The description of the group being created', location='form')
group_creation_args.add_argument('target', type=target, action='append', location='form', required=False, default=list)

group_query_args = page_args.copy()
group_query_args.add_argument('id', type=str, help='The id of the group', location='args', default='')
group_query_args.add_argument('name', type=str, help='The name of the group', location='args', default='')

group_update_args = reqparse.RequestParser()
group_update_args.add_argument('name', type=StrLen(50), help='The new name of the group being updated', location='form')
group_update_args.add_argument('desc', type=StrLen(lenght=200, min=0), help='The new description of the group being updated', location='form')

target_query_args = page_args.copy()
target_query_args.add_argument('target_id', type=str, help='The id of the target', location='args', default='')
target_query_args.add_argument('name', type=str, help='The name of the target', location='args', default='')
target_query_args.add_argument('person_code', type=str, help='The person code of the target', location='args', default='')
target_query_args.add_argument('email', type=str, help='The email of the target', location='args', default='')

target_creation_args = reqparse.RequestParser()
target_creation_args.add_argument('name', type=StrLen(50), help='The name of the target being created', location='form', required = True)
target_creation_args.add_argument('person_code', type=StrLen(25, 1), help='The person code of the target being created', location='form', required = True)
target_creation_args.add_argument('email', type=email, help='The email of the target being created', location='form', required = True)

@ns.route('/')
class Group(Resource):
    @jwt_required()
    @ns.doc(security='bearerAuth')
    @ns.expect(group_query_args)
    def get(self):
        args = group_query_args.parse_args(strict=True)
        page = GroupService(current_user.id).get_page_filtered(page=args['page'], per_page=args['per_page'], name=args['name'], id=args['id'])
        return make_response(page, 200)

    @jwt_required()
    @ns.doc(security='bearerAuth')
    @ns.expect(group_creation_args)
    def post(self):
        args = group_creation_args.parse_args(strict=True)
        # Check if there is duplicated emails
        hash_bucket = set()
        for item in args.get('target'):
            if item['email'] in hash_bucket:
                abort(400, message='Validation error', error={'email': f'Email {item['email']} is duplicated'})
            hash_bucket.add(item['email'] )
        # Initiate services
        group_service = GroupService(current_user.id)
        target_service = TargetService(current_user.id)
        # Add group
        try: 
            group = group_service.create(commit=False,
                name=args['name'],
                description=args['desc']
                )
        except:
            group_service.rollback()
            abort(500, message='Coudnt create group. All operations aborted!', error='Internal error')
        # Add targets
        try: 
            targets = target_service.create_many(commit=False,
                group_id=group['id'],
                items=args['target'])
        except:
            group_service.rollback()
            abort(500, message='Coudnt create targets. All operations aborted!', error='Internal error')

        # Commit changes
        group_service.commit()
        # Return created models
        return make_response(jsonify(group=group, targets=targets), 201)

@ns.route('/<int:id>')        
class GroupId(Resource):
    @jwt_required()
    @ns.doc(security='bearerAuth')
    def get(self, id):
        try:
            group = GroupService(current_user.id).get_by_id(id=id)
            if not group:
                raise PermissionError
            return make_response(group, 200)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})

    
    @jwt_required()
    @ns.doc(security='bearerAuth')
    @ns.expect(group_update_args)
    def patch(self, id):
        args = group_update_args.parse_args(strict=True)
        try:
            group = GroupService(current_user.id).update(
                id=id,
                name=args['name'],
                description=args['desc'])
            return make_response(group, 200)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except:
            return abort(500, message='Coudnt update group', error='Internal Error')
    
    @jwt_required()
    @ns.doc(security='bearerAuth')
    def delete(self, id):
        try:
            group = GroupService(current_user.id).delete(id)
            return make_response(group, 200)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except RuntimeError:
            return abort(400, message='Group cant be deleted', error={'group':'Group has a campaign active right now'})
        except:
            return abort(500, message='Coudnt delete group', error='Internal Error')
        

@ns.route('/<int:id>/target')        
class GroupTarget(Resource):
    @jwt_required()
    @ns.doc(security='bearerAuth')
    @ns.expect(target_query_args)
    def get(self, id):
        args = target_query_args.parse_args(strict=True)

        page = TargetService(current_user.id).get_page_filtered(
            page=args['page'],
            per_page=args['per_page'],
            exact={'group_id':id},
            id=args['target_id'],
            person_code=args['person_code'],
            name=args['name'],
            email=args['email'])
        return make_response(page, 200)

    @jwt_required()
    @ns.doc(security='bearerAuth')
    @ns.expect(target_creation_args)
    def post(self, id):
        args = target_creation_args.parse_args(strict=True)
        
        try:
            target = TargetService(current_user.id).create(
                group_id=id,
                name=args['name'],
                person_code=args['person_code'],
                email=args['email'])
            return make_response(target, 201)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except ValueError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except RuntimeError:
            return abort(400, message='Target cant be added', error={'Group has a campaign active right now'})
        except FileExistsError as e:
            if e.args:
                if e.args[0] == 'email':
                    return abort(400, message='Target cant be updated', error={'email':'Email already in use in that group'})
                elif e.args[0] == 'code':
                    return abort(400, message='Target cant be updated', error={'person_code':'Person code already in use in that group'})
            return abort(500, message='Coudnt update target', error='Internal Error')
        except:
            return abort(500, message='Coudnt update target', error='Internal Error')