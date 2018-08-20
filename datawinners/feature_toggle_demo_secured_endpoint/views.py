# Create your views here.
from waffle.decorators import waffle_flag
from django.http import HttpResponse
import json

@waffle_flag('secured_view', 'dashboard')
def secured_view(request):
   response_message = dict(status='success',message='This endpoint is available only for clients with secured_view enabled.') 
   return HttpResponse(content_type='application/json', content=json.dumps(response_message)) 
    