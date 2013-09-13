from django.http import Http404


def method_splitter(request, *args, **kwargs):
    get_view = kwargs.pop('GET', None)
    post_view = kwargs.pop('POST', None)
    if request.method == 'GET' and get_view is not None:
        return get_view(request, *args, **kwargs)
    elif request.method == 'POST' and post_view is not None:
        return post_view(request, *args, **kwargs)
    raise Http404

def append_query_strings_to_url(url, **query_parameters):
    query_string = ""
    for key,value in query_parameters.items():
        query_string += "%s=%s&" % (key, value)
    query_string = query_string.rstrip('&')
    return "%s?%s" % (url, query_string)
