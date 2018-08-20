import json
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.utils.http import int_to_base36
from datawinners.accountmanagement.decorators import is_super_admin
from datawinners.sms.models import SMS
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from mangrove.datastore.documents import FormModelDocument
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from datawinners.search.mapping import is_mapping_out_of_sync
import jsonpickle
from datawinners.settings import ELASTIC_SEARCH_HOST, ELASTIC_SEARCH_PORT
from elasticsearch.client import Elasticsearch
from elasticsearch_dsl.search import Search
from mangrove.datastore.cache_manager import get_cache_manager
from celery.bin.celery import result
import time
import math
from datawinners.search.submission_index_task import async_reindex, async_fetch_questionnaires, async_fetch_questionnaire_details
from celery import chain


reindex_in_cache_key = 'indexes_out_of_sync'
reindex_in_progress_cache_key = 'reindex_in_progress'


@is_super_admin
def generate_token_for_datasender_activate(request):
    user = User.objects.get(username=request.POST['ds_email'])
    token = default_token_generator.make_token(user)
    return HttpResponse(json.dumps({'token': token, 'user_id': int_to_base36(user.id)}),
                        content_type='application/json')

@is_super_admin
def check_if_datasender_entry_made_in_postgres(request):
    try:
        user_count = User.objects.filter(email__in=[request.POST['ds_email']]).count()
        found = True if user_count > 0 else False
    except Exception:
        found = False
    return HttpResponse(json.dumps({'found': found}), content_type='application/json')

@is_super_admin
def check_if_message_is_there_in_postgres(request):
    try:
        message_count = SMS.objects.filter(message=request.POST['message']).count()
        found = True if message_count > 0 else False
    except Exception:
        found = False
    return HttpResponse(json.dumps({'found': found}), content_type='application/json')


@staff_member_required
def reindex(request):
    response = dict()
    if (request.GET.get('reload')):
        response['reload'] = request.GET.get('reload')
    if (request.GET.get('full_reindex')):
        response['full_reindex'] = request.GET.get('full_reindex')
        
    return render_to_response("admin/reindex_elasticsearch.html", response,
                          context_instance=(RequestContext(request)))

@staff_member_required
def start_reindex(request):
    reindex_in_progress_cache = _get_from_cache(reindex_in_progress_cache_key)
    if not reindex_in_progress_cache:
        reindex_start_time = time.time()
        reindex_in_progress_cache = dict(start_time = reindex_start_time)
        reindex_catalog = _get_from_cache(reindex_in_cache_key)
        reindex_catalog['reindex_start_time'] = reindex_start_time
        list_of_indexes = reindex_catalog.get('list_of_indexes')
        for i, info in enumerate(list_of_indexes):
            if isinstance(info, dict) and info.get('questionnaire_id'):
                result = async_reindex.apply_async((info['db_name'], info['questionnaire_id']), countdown=5, retry=False)
                info['async_result'] = result
            list_of_indexes[i] = info
        _set_in_cache(reindex_in_progress_cache_key, reindex_in_progress_cache)
        _set_in_cache(reindex_in_cache_key, reindex_catalog)

    return render_to_response("admin/reindex_elasticsearch.html",{},
                              context_instance=(RequestContext(request)))

def reindex_status(request):
    return render_to_response("admin/reindex_elasticsearch.html",{},
                              context_instance=(RequestContext(request)))

def _get_from_cache(cache_key):
    cache_manager = get_cache_manager()
#     cache_key = 'indexes_out_of_sync'
    return cache_manager.get(cache_key)
    
def _set_in_cache(cache_key, value):
    cache_manager = get_cache_manager()
    cache_manager.set(cache_key, value)
                
def list_of_indexes_out_of_sync(request):
    reload_data = request.GET.get('reload')
    full_reindex = request.GET.get('full_reindex')
    reindex_catalog = _get_from_cache(reindex_in_cache_key)
    
    #Load questionnaires
    if reindex_catalog is None or reload_data or full_reindex:
        reindex_catalog = {}
        reindex_catalog['questionnaires_in_progress'] = async_list_of_indexes_to_reindex(full_reindex=full_reindex)
        _set_in_cache(reindex_in_cache_key, reindex_catalog)
        _set_in_cache(reindex_in_progress_cache_key, dict())
        return _questionnaire_loading_in_progress(reindex_catalog)
    elif _is_questionnaire_details_in_progress(reindex_catalog):
        return _questionnaire_loading_in_progress(reindex_catalog)
    elif reindex_catalog.get('questionnaires_in_progress'):
        reindex_catalog['list_of_indexes'] = _display_questionnaire_details_in_progress(reindex_catalog['questionnaires_in_progress'])
        reindex_catalog['total_submissions'] = _compute_total_submissions(reindex_catalog['list_of_indexes'])
        reindex_catalog.pop('questionnaires_in_progress')
        _set_in_cache(reindex_in_cache_key, reindex_catalog)

    #Update with reindex status, if started
    response_data, completed_submissions = _display_format(reindex_catalog['list_of_indexes'])
    in_progress = any([state.get('status','') == 'PENDING' for state in response_data])
    reindex_end_time_str = ''
    if not in_progress:
        end_times = [record.get('end_time_epoch') for record in response_data]
        reindex_end_time = max(end_times) if end_times else None
        if reindex_end_time:
            reindex_end_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reindex_end_time))
    reindex_start_time = reindex_catalog.get('reindex_start_time')
    reindex_start_time_str = ''
    if reindex_start_time:
        reindex_start_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(reindex_start_time))
    
    return HttpResponse(
        jsonpickle.encode(
            {
                'data': response_data,
                'in_progress': in_progress,
                'total_submissions': reindex_catalog['total_submissions'],
                'completed_submissions': completed_submissions,
                'reindex_start_time':reindex_start_time_str,
                'reindex_end_time':reindex_end_time_str,
                
            }, unpicklable=False), content_type='application/json')
    
def _questionnaire_loading_in_progress(reindex_catalog):
    response_data = _display_questionnaire_details_in_progress(reindex_catalog['questionnaires_in_progress'])
    return HttpResponse(
        jsonpickle.encode(
            {
                'data': response_data,
                'in_progress': True,                    
            }, unpicklable=False), content_type='application/json')
        

def _display_questionnaire_details_in_progress(results):
    response_data = []
    for result in results:
        if result.ready() and result.result:
            response_data.extend(result.result)
    return response_data
        
    
def _is_questionnaire_details_in_progress(reindex_catalog):
    results = reindex_catalog.get('questionnaires_in_progress')
    if not results:
        return False
    return any([result.ready() == False for result in results])
    
def _compute_total_submissions(indexes):
    try:
        return sum([index.get('no_of_submissions') for index in indexes])
    except:
        return 0
                        
def _display_format(indexes_out_of_sync):
    response_data = []
    completed_submissions = 0
    for reindex_info in indexes_out_of_sync:
        if isinstance(reindex_info, dict) and reindex_info.get('questionnaire_id'):
            record = dict(
                          db_name=reindex_info['db_name'], 
                          questionnaire_id=reindex_info['questionnaire_id'],
                          name=reindex_info['name'],
                          no_of_submissions=reindex_info['no_of_submissions'],
                          )
            async_result = reindex_info.get('async_result')
            if async_result:
                record['status'] = async_result.state
                record['result'] = async_result.result.__str__() if async_result.failed() else ''
                successful_result = async_result.result if async_result.successful() and async_result.result else {}
                if successful_result.get('end_time'):
                    end_time = successful_result.get('end_time')
                    record['end_time_epoch'] = end_time
                    record['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
                    completed_submissions += reindex_info['no_of_submissions']
                record['time_taken'] = math.ceil(successful_result.get('end_time',0)) - math.ceil(successful_result.get('start_time',0))
                
                
            response_data.append(record)
    return response_data, completed_submissions
        
def async_list_of_indexes_to_reindex(full_reindex=False):
    questionnaire_details_task_results = []
    db_names = all_db_names()
    for db_name in db_names:
        chain_obj = chain(async_fetch_questionnaires.s(db_name, full_reindex) | async_fetch_questionnaire_details.s(db_name, full_reindex))
        result = chain_obj.apply_async()
        questionnaire_details_task_results.append(result)
    return questionnaire_details_task_results

def get_list_of_indexes_to_reindex(full_reindex=False):
    db_names = all_db_names()
    try:
        list_of_indexes_out_of_sync = []
        total_submissions = 0
        for database_name in db_names:
            dbm = get_db_manager(database_name)
            questionnaires = dbm.load_all_rows_in_view('questionnaire')
            if not questionnaires:
                continue
            for row in questionnaires:
                if row['value']['is_registration_model']:
                    continue
                
                form_model_doc = FormModelDocument.wrap(row["value"])
                if full_reindex or is_mapping_out_of_sync(form_model_doc, dbm):
                    es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
                    search = Search(using=es, index=dbm.database_name, doc_type=form_model_doc.id)
                    no_of_submissions = search.count()
                    questionnaire_info = dict(
                                              db_name = database_name,
                                              questionnaire_id=form_model_doc.id,
                                              name=form_model_doc.name,
                                              no_of_submissions = no_of_submissions)
                    total_submissions += no_of_submissions
                    list_of_indexes_out_of_sync.append(questionnaire_info)
        return list_of_indexes_out_of_sync, total_submissions
    except Exception as e:
        pass
    
