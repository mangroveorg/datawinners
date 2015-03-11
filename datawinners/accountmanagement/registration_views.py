from django.utils.translation import activate
from registration.views import register


def get_previous_page_language(request):
    if request.META.has_key('HTTP_REFERER'):
        url = request.META.get('HTTP_REFERER')

        slash_parts = url.split('/')

        if len(slash_parts) < 4:
            return

        language = slash_parts[3]
        if request.META['HTTP_HOST'] != slash_parts[2]:
            if language not in ["en", "fr"]:
                language = "en"

            request.session['django_language'] = language
            activate(language)

def register_view(request, form_class=None, template_name=None,
                         backend=None, language=None):
        if language:
            request.session['django_language'] = language
            activate(language)
        return register(request, backend, form_class=form_class,
             template_name=template_name)

  