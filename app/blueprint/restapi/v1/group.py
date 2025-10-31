from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, current_user
from flask import jsonify
from . import StrLen, target, page_args
from service.group_service import GroupService
from service.target_service import TargetService

ns = Namespace('Group', 'Target group crud operations', path='/group')

group_creation_args = reqparse.RequestParser()
group_creation_args.add_argument("name", type=StrLen(25), help="The name of the group being created", location='form', required=True)
group_creation_args.add_argument("desc", type=StrLen(lenght=50, min=0), help="The description of the group being created", location='form', default='', required=False)
group_creation_args.add_argument("target", type=target, action='append', location="form", required=False, default=list)

group_update_args = reqparse.RequestParser()
group_update_args.add_argument("name", type=StrLen(25), help="The new name of the group being updated", location='form', default='', required=False)
group_update_args.add_argument("desc", type=StrLen(lenght=50, min=0), help="The new description of the group being updated", location='form', default='', required=False)

@ns.route('/')
class Group(Resource):
    @jwt_required()
    @ns.expect(group_creation_args, validate=True)
    def post(self):
        args = group_creation_args.parse_args()

        # Check if there is duplicated emails
        hash_bucket = set()
        for item in args.get('target'):
            if item['email'] in hash_bucket:
                abort(400, error={'email': f'Email {item['email']} is duplicated'})
            hash_bucket.add(item['email'] )

        # Initiate services
        group_service = GroupService()
        target_service = TargetService()

        # Add group
        try: 
            group = group_service.create(commit=False,
                creator_id=current_user.id,
                name=args['name'],
                description=args['desc']
                )
        except:
            abort(400, 'Coudnt create group. All operations aborted!')

        # Add targets

        targets = target_service.create_many(commit=False,
            creator_id=current_user.id,
            group_id=group['id'],
            items=args['target'])

        # Commit changes
        group_service.commit()
        # Return created models
        return jsonify(group=group, targets=targets)

    @jwt_required()
    @ns.expect(page_args)
    def get(self):
        args = page_args.parse_args()

        group_service = GroupService()
        return group_service.get_page_filtered(creator_id=current_user.id, page=args['page'], per_page=args['per_page'])

@ns.route('/<int:id>')        
class GroupId(Resource):
    @jwt_required()
    def get(self, id):
        group_service = GroupService()
        group = group_service.get_by_filter(id=id, creator_id=current_user.id, limit=1)
        if not group:
            return abort(404, message="Not Found", error={'id': 'Referenced id element not found'})
        return group[0]
    
    @jwt_required()
    def put(self, id):
        args = group_update_args.parse_args()
        
        group_service = GroupService()
        try:
            group = group_service.update(
                model_id=id,
                user_id=current_user.id,
                name=args['name'],
                description=args['desc'])
            return group
        except PermissionError:
            if not group:
                return abort(404, message="Not Found", error={'id': 'Referenced id element not found'})
