from main.utils import get_database_manager

class WebSMSDBMRequestProcessor(object):
    def process(self, request):
        request['dbm']=get_database_manager(request.user)
