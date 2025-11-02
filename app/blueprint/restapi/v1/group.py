from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, current_user
from flask import jsonify
from . import StrLen, target, page_args, email
from service.group_service import GroupService
from service.target_service import TargetService

ns = Namespace('Group', 'Target group crud operations', path='/group')

group_creation_args = reqparse.RequestParser()
group_creation_args.add_argument('name', type=StrLen(25), help='The name of the group being created', location='form', required=True)
group_creation_args.add_argument('desc', type=StrLen(lenght=50, min=0), help='The description of the group being created', location='form', default='')
group_creation_args.add_argument('target', type=target, action='append', location='form', required=False, default=list)

group_query_args = page_args.copy()
group_query_args.add_argument('name', type=str, help='The name of the group', location='args', default='')

group_update_args = reqparse.RequestParser()
group_update_args.add_argument('name', type=StrLen(25), help='The new name of the group being updated', location='form', default='')
group_update_args.add_argument('desc', type=StrLen(lenght=50, min=0), help='The new description of the group being updated', location='form', default='')

target_query_args = page_args.copy()
target_query_args.add_argument('name', type=str, help='The name of the target', location='args', default='')
target_query_args.add_argument('email', type=str, help='The email of the target', location='args', default='')

target_creation_args = reqparse.RequestParser()
target_creation_args.add_argument('name', type=StrLen(50), help='The name of the target being created', location='form', required = True)
target_creation_args.add_argument('email', type=email, help='The email of the target being created', location='form', required = True)

@ns.route('/')
class Group(Resource):
    @jwt_required()
    @ns.expect(group_query_args)
    def get(self):
        args = group_query_args.parse_args(strict=True)
        return GroupService(current_user.id).get_page_filtered(page=args['page'], per_page=args['per_page'], name=args['name'])

    @jwt_required()
    @ns.expect(group_creation_args)
    def post(self):
        args = group_creation_args.parse_args(strict=True)

        # Check if there is duplicated emails
        hash_bucket = set()
        for item in args.get('target'):
            if item['email'] in hash_bucket:
                abort(400, error={'email': f'Email {item['email']} is duplicated'})
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
        return jsonify(group=group, targets=targets)

@ns.route('/<int:id>')        
class GroupId(Resource):
    @jwt_required()
    def get(self, id):
        try:
            group = GroupService(current_user.id).get_by_id(id=id)
            if not group:
                return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
            return group
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
    
    @jwt_required()
    @ns.expect(group_update_args)
    def patch(self, id):
        args = group_update_args.parse_args(strict=True)
        
        try:
            group = GroupService(current_user.id).update(
                id=id,
                name=args['name'],
                description=args['desc'])
            return group
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
    
    @jwt_required()
    def delete(self, id):
        try:
            return GroupService(current_user.id).delete(id)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except RuntimeError:
            return abort(400, message='Group cant be deleted', error={'group':'Group has a campaing active right now'})
        

@ns.route('/<int:id>/target')        
class GroupTarget(Resource):
    @jwt_required()
    @ns.expect(target_query_args)
    def get(self, id):
        args = target_query_args.parse_args(strict=True)

        return TargetService(current_user.id).get_page_filtered(
            page=args['page'],
            per_page=args['per_page'],
            exact={'group_id':id},
            name=args['name'],
            email=args['email'])
    
    @jwt_required()
    @ns.expect(target_creation_args)
    def post(self, id):
        args = target_creation_args.parse_args(strict=True)
        
        try:
            return TargetService(current_user.id).create(group_id=id, name=args['name'], email=args['email'])
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except RuntimeError:
            return abort(400, message='Target cant be added', error={'group':'Group has a campaing active right now'})