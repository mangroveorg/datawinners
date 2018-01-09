# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re
import requests

from json import loads
from pprint import pprint

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from pymessenger import Bot


PAGE_ACCESS_TOKEN = "EAAFZCluSqoIYBAAtB2LTkCgQcjLpdssMbT1fsyiXhGGZBJYMwVSLOD2ZBh39jNkdRmHchAA7WKpQWYabzIXZBM0K9wuCvDxi6BT9wyntW0HUMqAW8yKJcVce8bhXdpibAbzGBThvNkgE5aHAli3uJHYv1ZBqVZAly9gFeKNd2cBAZDZD"
VERIFY_TOKEN = "tokitoki"

bot = Bot(PAGE_ACCESS_TOKEN)

questionnaires = {'ecole': ["""School Name. School Identification Number. Number of Students.""",
                            """string.string.number"""],
                  'sante': ["""Month and Year. Clinic name. Clinic Identification Number. Stock.""",
                            """date.string.string.number"""],
                  'agri': ["""Date of visit. Name of location visited. Type of Production.""",
                           """date.string.string"""]}


# Helper function
def post_facebook_message(fbid, received_message):
    tokens = re.sub(r"[^a-zA-Z0-9\s]", ' ', received_message).lower().split()
    response_text = ''
    number_of_tokens = len(tokens)
    if number_of_tokens == 1:
        try:
            response_text = questionnaires[tokens[0]][0]
        except KeyError:
            pass
    elif number_of_tokens > 1:
        try:
            questionnaire_template = questionnaires[tokens[0]][1]
            number_of_questions = len(questionnaire_template.split('.'))
            if number_of_tokens == (number_of_questions + 1):
                tokens.pop(0)
                received_tokens = '. '.join(tokens)
                response_text = "Thank you. We received: %s" % received_tokens
            else:
                response_text = "I didn't understand! Send '%s' for help :)" % tokens[0]
        except KeyError:
            pass

    if not response_text:
        response_text = "I didn't understand! Send 'help' for help :)"

    user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
    user_details_params = {'fields': 'first_name,last_name,profile_pic', 'access_token': PAGE_ACCESS_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()
    response_text = 'Yo ' + user_details['first_name'] + '! ' + response_text

    bot.send_text_message(fbid, response_text)


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
        incoming_message = loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                    post_facebook_message(message['sender']['id'], message['message']['text'])
        return HttpResponse()
