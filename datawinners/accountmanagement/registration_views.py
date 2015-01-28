from django.utils.translation import activate
from registration.views import register


def get_previous_page_language(request):
    if request.META.has_key('HTTP_REFERER'):
        url = request.META.get('HTTP_REFERER')

        slash_parts = url.split('/')
        language = slash_parts[3]
        if language in ["en", "fr"]:
            request.session['django_language'] = language
            previous_language = activate(language)
            return previous_language

def register_view(request, form_class=None, template_name=None,
                         backend=None):
    get_previous_page_language(request)
    return register(request, backend, form_class=form_class,
             template_name=template_name)

  