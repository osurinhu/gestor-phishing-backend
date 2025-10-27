from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, current_user
from flask import jsonify
from . import StrLen, target
from service.group_service import GroupService
from service.target_service import TargetService

import traceback

ns = Namespace('Group', 'Target group crud operations', path='/group')

group_args = reqparse.RequestParser()
group_args.add_argument("group_name", type=StrLen(25), help="The name of the group being created", location='form', required=True)
group_args.add_argument("group_desc", type=StrLen(lenght=50, min=0), help="The description of the group being created", location='form',  default='', required=False)
group_args.add_argument("group_target", type=target, action='append', location="form", required=False, default=list)

@ns.route('/')
class Group(Resource):

    @jwt_required()
    @ns.expect(group_args, validate=True)
    def post(self):
        args = group_args.parse_args()

        # Check if there is duplicated emails
        hash_bucket = set()
        for item in args.get('group_target'):
            if item['target_email'] in hash_bucket:
                abort(400, error={'target_email': f'Email {item['target_email']} is duplicated'})
            hash_bucket.add(item['target_email'] )

        # Initiate services
        group_service = GroupService()
        target_service = TargetService()

        # Add group
        try: 
            group = group_service.add_new_model(commit=False,
                creator_id=current_user.id,
                name=args['group_name'],
                description=args['group_desc']
                )
        except BaseException as e:
            abort(400, 'Coudnt create group', errors=str(e))

        # Add targets
        if args['group_target']:
            try:
                targets = target_service.add_many_new(commit=False,
                    creator_id=current_user.id,
                    group_id=group['id'],
                    items=args['group_target'])
            except Exception as e:
                abort(400, 'Coudnt create targets', errors=str(e))

        # Commit changes
        group_service.commit()

        # Return created models
        return jsonify(group=group, targets=targets)

    @jwt_required()
    def get(self):
        group_service = GroupService()
        groups=group_service.get_by_filter(creator_id=current_user.id)
        
        return jsonify(group=groups)
        
    



    
    



    