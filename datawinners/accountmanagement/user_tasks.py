from datawinners.tasks import app
from django.contrib.auth.models import User
from datawinners.main.database import get_database_manager
from datawinners.project.couch_view_helper import get_all_projects
from datawinners.accountmanagement.helper import make_user_data_sender_with_project
from celery import shared_task


@app.task(max_retries=3, throw=False)
def link_user_to_all_projects(user_id):
    user = User.objects.get(pk=user_id)
    reporter_id = user.get_profile().reporter_id
    manager = get_database_manager(user)
    rows = get_all_projects(manager)
    for row in rows:
        make_user_data_sender_with_project(manager, reporter_id, row['value']['_id'])

@app.task(max_retries=3, throw=False)
def link_user_to_some_projects(user_id, *projects):
    user = User.objects.get(pk=user_id)
    reporter_id = user.get_profile().reporter_id
    manager = get_database_manager(user)
    for projet in projects:
        make_user_data_sender_with_project(manager, reporter_id, projet)
    