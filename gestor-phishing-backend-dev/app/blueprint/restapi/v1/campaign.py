from flask_restx import Namespace, Resource, reqparse, abort
from flask_jwt_extended import jwt_required, current_user
from flask import make_response
from service.campaign_service import CampaignService
from . import StrLen, page_args, timeO, dateO, email



ns = Namespace('Campaign', 'Campaign crud operations', path='/campaign')

campaign_creation_args = reqparse.RequestParser()
campaign_creation_args.add_argument('group_id', type=int, help='ID of the group associated with this campaign', location='form', required=True)
campaign_creation_args.add_argument('template_id', type=int, help='ID of the email template used by the campaign', location='form', required=True)
campaign_creation_args.add_argument('name', type=StrLen(50), help='Name of the campaign', location='form', required=True)
campaign_creation_args.add_argument('desc', type=StrLen(lenght=200, min=0), help='Description of the campaign', location='form')
campaign_creation_args.add_argument("email", type=email, help="The sender email of the campaign", location="form", required=True)
campaign_creation_args.add_argument('start_date', type=dateO, help='Start date of the campaign (YYYY-MM-DD)', location='form', required=True)
campaign_creation_args.add_argument('end_date', type=dateO, help='End date of the campaign (YYYY-MM-DD)', location='form', required=True)
campaign_creation_args.add_argument('send_time', type=timeO, help='Time when the emails should be sent (HH:MM)', location='form', required=True)
campaign_creation_args.add_argument('subject_text', type=StrLen(50), help='Subject of the email', location='form', required=True)
campaign_creation_args.add_argument('title_text', type=StrLen(50), help='Title text of the email', location='form', required=True)
campaign_creation_args.add_argument('button_text', type=StrLen(50), help='Button text of the email', location='form', required=True)
campaign_creation_args.add_argument('body_text', type=StrLen(500), help='Body text of the email', location='form', required=True)

campaign_query_args = page_args.copy()
campaign_query_args.add_argument('id', type=str, help='The id of the campaign', location='args', default='')
campaign_query_args.add_argument('name', type=StrLen(50), help='Name of the campaign', location='args', default='')
campaign_query_args.add_argument('group_id', type=int, help='The target group of the campaign', location='args', default='')
campaign_query_args.add_argument('template_id', type=int, help='The template of the campaign', location='args', default='')
campaign_query_args.add_argument('start_date', type=dateO, help='Start date of the campaign (YYYY-MM-DD)', location='args', default='')
campaign_query_args.add_argument('end_date', type=dateO, help='End date of the campaign (YYYY-MM-DD)', location='args', default='')
campaign_query_args.add_argument('send_time', type=timeO, help='Time when the emails should be sent (HH:MM)', location='args', default='')
campaign_query_args.add_argument('status', type=StrLen(1,1), help='The status of the campaign', location='args', default='')

campaign_update_args = reqparse.RequestParser()
campaign_update_args.add_argument('group_id', type=int, help='ID of the group associated with this campaign', location='form')
campaign_update_args.add_argument('template_id', type=int, help='ID of the email template used by the campaign', location='form')
campaign_update_args.add_argument('name', type=StrLen(50), help='Name of the campaign', location='form')
campaign_update_args.add_argument('desc', type=StrLen(lenght=200, min=0), help='Description of the campaign', location='form')
campaign_update_args.add_argument("email", type=email, help="The sender email of the campaign", location="form")
campaign_update_args.add_argument('start_date', type=dateO, help='Start date of the campaign (YYYY-MM-DD)', location='form')
campaign_update_args.add_argument('end_date', type=dateO, help='End date of the campaign (YYYY-MM-DD)', location='form')
campaign_update_args.add_argument('send_time', type=timeO, help='Time when the emails should be sent (HH:MM)', location='form')
campaign_update_args.add_argument('subject_text', type=StrLen(50), help='Subject of the email', location='form')
campaign_update_args.add_argument('title_text', type=StrLen(50), help='Title text of the email', location='form')
campaign_update_args.add_argument('button_text', type=StrLen(50), help='Button text of the email', location='form')
campaign_update_args.add_argument('body_text', type=StrLen(500), help='Body text of the email', location='form')


@ns.route('/')
class Campaign(Resource):
    @jwt_required()
    @ns.doc(security='bearerAuth')
    @ns.expect(campaign_query_args)
    def get(self):
        args = campaign_query_args.parse_args(strict=True)
        page = CampaignService(current_user.id).get_page_filtered(
            page=args['page'], per_page=args['per_page'], extra_fields=('group.name', 'template.name'),
            id=args['id'],
            name=args['name'],
            group_id=args['group_id'],
            template_id=args['template_id'],
            start_date=args['start_date'],
            end_date=args['end_date'],
            send_time=args['send_time'],
            status=args['status']
        )
        return make_response(page, 200)

    @jwt_required()
    @ns.doc(security='bearerAuth')
    @ns.expect(campaign_creation_args)
    def post(self):
        args = campaign_creation_args.parse_args(strict=True)

        try:
            campaign = CampaignService(current_user.id).create(
                group_id=args['group_id'],
                template_id=args['template_id'],
                name=args['name'],
                description=args['desc'],
                start_date=args['start_date'],
                end_date=args['end_date'],
                send_time=args['send_time'],
                subject_text=args['subject_text'],
                title_text=args['title_text'],
                body_text=args['body_text'],
                button_text=args['button_text'],

            )
            return make_response(campaign, 201)
        except ValueError as e:
            if e.args:
                if e.args[0] == 'endstart':
                    return abort(400, message='Validation error', error={'dates':'End date should be later than start date'})
                if e.args[0] == 'startpast':
                    return abort(400, message='Validation error', error={'dates':'Start date should be in the future'})
                if e.args[0] == 'endpast':
                    return abort(400, message='Validation error', error={'dates':'End date should be in the future'})
                elif e.args[0] == 'group':
                    return abort(400, message='Validation error', error={'group':'Referenced id element not found'})
                elif e.args[0] == 'template':
                    return abort(400, message='Validation error', error={'template':'Referenced id element not found'})
            return abort(500, message='Coudnt create campaign', error='Internal Error')
        except:
            return abort(500, message='Coudnt create campaign', error='Internal Error')

@ns.route('/<int:id>')        
class CampaignId(Resource):
    @jwt_required()
    @ns.doc(security='bearerAuth')
    def get(self, id):
        try:
            group = CampaignService(current_user.id).get_by_id(id=id, extra_fields=('send_time','subject_text','title_text','template.name','group.name'))
            return make_response(group, 200)
        except PermissionError:
            return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except:
            return abort(500, message='Coudnt get campaign', error='Internal Error')
        
    @jwt_required()
    @ns.doc(security='bearerAuth')
    @ns.expect(campaign_update_args)
    def patch(self, id):
        args = campaign_update_args.parse_args(strict=True)
        try:
            group = CampaignService(current_user.id).update(
                id=id,
                group_id=args['group_id'],
                template_id=args['template_id'],
                name=args['name'],
                description=args['desc'],
                start_date=args['start_date'],
                end_date=args['end_date'],
                send_time=args['send_time'],
                subject_text=args['subject_text'],
                title_text=args['title_text'],
                body_text=args['body_text'],
                button_text=args['button_text']
                )
            return make_response(group, 200)
        except ValueError as e:
            if args[0] == 'date':
                return abort(400, message='Validation error', error={'dates':'Start date bigger than end date'})
            elif args[0] == 'group':
                return abort(400, message='Validation error', error={'group':'Referenced id element not found'})
            elif args[0] == 'template':
                return abort(400, message='Validation error', error={'template':'Referenced id element not found'})
        except PermissionError as e:
            if e.args:
                if e.args['active']:
                    return abort(423, message='Campaign is unavailable, cant perform changes')
                else:
                    abort(423)
            else:
                return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except:
            return abort(500, message='Coudnt update campaign', error='Internal Error')

    @jwt_required()
    @ns.doc(security='bearerAuth')
    def delete(self, id):
        try:
            group = CampaignService(current_user.id).delete(id)
            return make_response(group, 200)
        except PermissionError as e:
            if e.args:
                if e.args['active']:
                    return abort(423, message='Campaign is unavailable, cant perform changes')
                else:
                    abort(423)
            else:
                return abort(404, message='Not Found', error={'id': 'Referenced id element not found'})
        except:
            return abort(500, message='Coudnt delete campaign', error='Internal Error')