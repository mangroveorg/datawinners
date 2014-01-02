from celery import Celery

app = Celery('tasks', backend='amqp', broker='amqp://guest@127.0.0.1:5672//', include=['datawinners.project.wizard_view'])
