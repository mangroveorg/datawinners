# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
import requests
import uuid
import re

from django.http import HttpResponse, QueryDict
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.urlresolvers import reverse
from mangrove.errors.MangroveException import MangroveException
from django.contrib.auth.models import User
from datawinners.main.database import get_database_manager
from datawinners.project.view_models import ReporterEntity
from mangrove.form_model.form_model import REPORTER
from mangrove.datastore.entity import get_by_short_code
from mangrove.errors.MangroveException import DataObjectNotFound
from accountmanagement.models import NGOUserProfile
from accountmanagement.models import Organization
from accountmanagement.models import OrganizationSetting

from atom.http_core import HttpRequest

from datawinners.submission.views import sms

PAGE_ACCESS_TOKEN = "EAAFZCluSqoIYBANjdNs6HiWq95J19QDcZBTHCAeAZBHQcd2CEhgNOEyU3bsXRnsIDzUlIt9VTNtqu7jmKmtl5ohy6qE6SzNUCN2xPpwjXk6wrnbokyIu9y03CFYqwCkuPEOkRyhLZA5Yh0oVIeDAz1GyuvZB6Dbb9uthHmLYCGQZDZD"
VERIFY_TOKEN = "tokitoki"


# Helper function
def post_facebook_message(fbid, received_message):
    response_text = ""
    keywords = received_message.lower().split()
    if keywords[0] == 'activate':
        if len(keywords) == 4:
            try:
                user = User.objects.get(email=keywords[2])
                manager = get_database_manager(user)
                reporter_entity = ReporterEntity(get_by_short_code(manager, keywords[1], [REPORTER]))
                if reporter_entity.email == user.email and reporter_entity.mobile_number == keywords[3]:
                    try:
                        ds = NGOUserProfile.objects.get(fb_id=fbid)
                        ds.fb_id = ''
                        ds.save()
                    finally:
                        datasender = NGOUserProfile.objects.get(user=user)
                        datasender.fb_id = fbid
                        datasender.save()
                        response_text = 'ID saved for ' + reporter_entity.name
                else:
                    response_text = 'Credentials do not match'
            except User.DoesNotExist as e:
                #response_text = e.message
                response_text = 'User with that email address has not been found'
            except DataObjectNotFound as e:
                #response_text = e.message
                response_text = 'User with that ID has not been found'
            except NGOUserProfile.DoesNotExist as e:
                #response_text = e.message
                response_text = 'No datasender with those credentials found'
        else:
            response_text = 'Please send your ID, email and mobile phone number.'
    else:
        try:
            ds = NGOUserProfile.objects.get(fb_id=fbid)
            organization = Organization.objects.get(org_id=ds.org_id)
            organization_settings = OrganizationSetting.objects.get(organization=organization)
            _message = received_message
            _from = ds.mobile_phone
            _to = organization_settings.sms_tel_number
            _to = _to.split(',')[0]
            _from = _from.split(',')[0]
            submission_request = HttpRequest(uri=reverse(sms), method='POST')
            if settings.USE_NEW_VUMI:
                submission_request.POST = {"content": _message, "from_addr": _from, "to_addr": _to, "message_id":uuid.uuid1().hex}
            else:
                submission_request.POST = {"message": _message, "from_msisdn": _from, "to_msisdn": _to, "message_id":uuid.uuid1().hex}

            try:
                #response = sms(submission_request)
                #response_text = re.sub(r'SMS', 'message',response.content)
                response_text = 'Got it!'
            except:
                response_text = 'There was an error.'

        except MangroveException as exception:
            response_text = exception.message
        except NGOUserProfile.DoesNotExist:
            response_text = "Facebook account not yet activated."
        except Organization.DoesNotExist as exception:
            response_text = exception.message

    params = {
        "access_token": "EAAFZCluSqoIYBANjdNs6HiWq95J19QDcZBTHCAeAZBHQcd2CEhgNOEyU3bsXRnsIDzUlIt9VTNtqu7jmKmtl5ohy6qE6SzNUCN2xPpwjXk6wrnbokyIu9y03CFYqwCkuPEOkRyhLZA5Yh0oVIeDAz1GyuvZB6Dbb9uthHmLYCGQZDZD"
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": fbid
        },
        "message": {
            "text": response_text
        }
    })
    requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)


# Create your views here.
class BotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = dict(self.request.POST.iterlists())
        incoming_message = next(iter(incoming_message))
        incoming_message = json.loads(incoming_message)
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events
                if 'message' in message:
                    # Print the message to the terminal
                    #pprint(message)
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()
