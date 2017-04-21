from celery import Celery

app = Celery('tasks', backend='amqp', broker='amqp://guest@127.0.0.1:5672//',
             include=['datawinners.project.wizard_view', 'datawinners.search.submission_index_task',
                      'datawinners.entity.datasender_tasks', 'datawinners.blue.xform_edit.submission',
                      'datawinners.accountmanagement.user_tasks'])

app.conf.update(
    CELERYD_POOL_RESTARTS=True,
    CELERYD_LOG_COLOR=True,
)
