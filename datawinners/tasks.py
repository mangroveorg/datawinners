from celery import Celery
from celery.app.control import Inspect
app = Celery('tasks', backend='amqp', broker='amqp://guest@127.0.0.1:5672//', include=['datawinners.project.wizard_view','datawinners.search.submission_index_task'])

app.conf.update(
    CELERYD_POOL_RESTARTS=True,
    CELERYD_LOG_COLOR=True,
)
