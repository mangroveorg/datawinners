# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
import requests
import uuid

from json import loads

from django.http import HttpResponse, QueryDict
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.urlresolvers import reverse
from mangrove.errors.MangroveException import MangroveException

from atom.http_core import HttpRequest

from datawinners.submission.views import sms


#PAGE_ACCESS_TOKEN = settings.__getattr__('PAGE_ACCESS_TOKEN')
PAGE_ACCESS_TOKEN = 'EAAFZCluSqoIYBAHMr9711zvXF98tdLRGx8CoPyQFWXjrf5Q6pvFMTMi3OZB6uwxaG2PX0NR0mTtNNsv5Trb9SZBvPBZAU20ITBGW6eA9IZAnfBkrkmEIcZBaG6yxCjw1Q5Oz3PRAJb2BxHo5VFyFzmv1a6I3EREWtGZAejBHRpK7QZDZD'
#VERIFY_TOKEN = settings.__getattr__('VERIFY_TOKEN')
VERIFY_TOKEN = 'tokitoki'

questionnaires = {'ecole': ["""School Name. School Identification Number. Number of Students.""",
                            """string.string.number"""],
                  'sante': ["""Month and Year. Clinic name. Clinic Identification Number. Stock.""",
                            """date.string.string.number"""],
                  'agri': ["""Date of visit. Name of location visited. Type of Production.""",
                           """date.string.string"""]}


def post_facebook_message(fbid, received_message):
    _message = received_message
    _from = '123456789'
    _to = '0323200534'
    try:
        submission_request = HttpRequest(uri=reverse(sms), method='POST')
        if settings.USE_NEW_VUMI:
            submission_request.POST = {"content": _message, "from_addr": _from, "to_addr": _to, "message_id":uuid.uuid1().hex}
        else:
            submission_request.POST = {"message": _message, "from_msisdn": _from, "to_msisdn": _to, "message_id":uuid.uuid1().hex}

        response = sms(submission_request)
        message = response.content

    except MangroveException as exception:
        message = exception.message
    response_text = message

    #user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
    #user_details_params = {'fields': 'first_name,last_name,profile_pic', 'access_token': PAGE_ACCESS_TOKEN}
    #user_details = requests.get(user_details_url, user_details_params).json()
    #response_text = 'Yo ' + user_details['first_name'] + '! ' + response_text

    params = {
        "access_token": "EAAFZCluSqoIYBAHMr9711zvXF98tdLRGx8CoPyQFWXjrf5Q6pvFMTMi3OZB6uwxaG2PX0NR0mTtNNsv5Trb9SZBvPBZAU20ITBGW6eA9IZAnfBkrkmEIcZBaG6yxCjw1Q5Oz3PRAJb2BxHo5VFyFzmv1a6I3EREWtGZAejBHRpK7QZDZD"
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

    #post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    #response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":"response_text"}})
    #requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)

    #bot.send_text_message(fbid, response_text)


class BotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        try:
            return generic.View.dispatch(self, request, *args, **kwargs)
        except:
            return None

    def post(self, request, *args, **kwargs):
        data = dict(self.request.POST.iterlists())
        data = next(iter(data))
        data = loads(data)

        if data['object'] == 'page':
            for entry in data['entry']:
                for messaging_event in entry['messaging']:

                    # IDs
                    sender_id = messaging_event['sender']['id']
                    recipient_id = messaging_event['recipient']['id']

                    if messaging_event.get('message'):
                        # Extracting text message
                        if 'text' in messaging_event['message']:
                            messaging_text = messaging_event['message']['text']
                        else:
                            messaging_text = 'no text'

                        post_facebook_message(sender_id, messaging_text)

        #incoming_message = dict(self.request.POST.iterlists())
        #incoming_message = next(iter(incoming_message))
        #incoming_message = loads(incoming_message)
        #for entry in incoming_message['entry']:
        #    for message in entry['messaging']:
        #        if 'message' in message:
        #            post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()
