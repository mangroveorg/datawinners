__Getting started__

##Recommended technical resources

__Git__

Datawinners uses [Git](git-scm.com) for source code control. Familiarize with
basic Git workflow. Please check out below articles.
 * http://git-scm.com/book/en/Getting-Started-Installing-Git
 * https://help.github.com/categories/19/articles
 * https://www.atlassian.com/git/workflows
 * http://blog.apiaxle.com/post/handy-git-tips-to-stop-you-getting-fired/

__Python__
 * http://c2.com/cgi/wiki?PythonPhilosophy
 * http://www.youtube.com/watch?v=OSGv2VnC0go


__Python Django application framework.__

  Python django supports different aspects of web application like authentication,
  persistance, templating etc. Django derives some part of python philosophy one can

  Try and learn django application basics https://docs.djangoproject.com/en/dev/intro/

__Couchdb__

Datawinners uses couchdb for enabling multi-tenant datastore for questionnaires
and submissions. Its document structure and views gives light weight datastore.


__Elastic Search__

For extensive search datawinners relies on elastic search, which is based on
apache lucene. Elastic search is known for scalability and reliability.

__Rabit MQ__

All time-consuming batch tasks are handled via message queues. Python binding
mq binding is easy to use and integrates well with celery.

__supervisord__
supervisor is process management utility, helps in deamonizing processes and restarting if it dies. Datawinners reminder script triggered via supervisor. In vumi all workers and transport consumers are started by supervisor.


