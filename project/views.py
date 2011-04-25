# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import helper
@login_required(login_url='/login')

def questionnaire(request):

    return render_to_response('project/questionnaire.html', context_instance=RequestContext(request))

def save_questionnaire(request):
#    if request.POST:

    print "hello world"
    print request.POST
#    q_list=helper.create_question_list(request.POST)
#    #Build Questions
    #Todo Check for type of each in q_list and generate Integer Q/ Text Q etc

    #questionnaire = Questionnaire(get_db_manager(), entity_id = "Tadaaaaaaa!",name="aids", label="Aids Questionnaire",
#                                  questionnaire_code="1",type='survey',questions=question_list)
#    print questionnaire
#    questionnaire__id = questionnaire.save()
#    return HttpResponse('Saved')

#    return render_to_response('')
#
#    question_list = request.question_list
#    for each in question_list
#       q_list= QuestionBuilder(each)
#    Questionnaire(q_list).save

