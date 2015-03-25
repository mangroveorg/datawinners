# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import re
from datetime import datetime
import random
import unicodedata

from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _, activate, get_language
from django.contrib.auth.forms import PasswordResetForm

from datawinners import settings
from datawinners.main.database import get_db_manager


VAR = "HNI"

def sorted_unique_list(value_list):
    return sorted(list(set(value_list)))


def get_database_manager_for_org(organization):
    from datawinners.accountmanagement.models import OrganizationSetting

    organization_settings = OrganizationSetting.objects.get(organization=organization)
    return get_db_manager(organization_settings.document_store)


def get_organization(request):
    from datawinners.accountmanagement.models import Organization

    profile = request.user.get_profile()
    return Organization.objects.get(org_id=profile.org_id)


def get_organization_country(request):
    return get_organization(request).country_name()


def convert_to_ordinal(number):
    if 10 < number < 14: return _('%dth') % number
    if number % 10 == 1: return _('%dst') % number
    if number % 10 == 2: return _('%dnd') % number
    if number % 10 == 3: return _('%drd') % number
    return _('%dth') % number


def generate_document_store_name(organization_name, organization_id):
    return slugify("%s_%s_%s" % (VAR, organization_name, organization_id))


def get_organization_settings_from_request(request):
    from datawinners.accountmanagement.models import OrganizationSetting

    return OrganizationSetting.objects.get(organization=get_organization(request))


def get_organization_from_manager(manager):
    from datawinners.accountmanagement.models import Organization, OrganizationSetting

    setting = OrganizationSetting.objects.get(document_store=manager.database_name)
    organization = Organization.objects.get(org_id=setting.organization_id)
    return organization

def get_organization_language(manager):
    organization = get_organization_from_manager(manager)
    return organization.language

def send_reset_password_email(user, language_code):
    reset_form = PasswordResetForm({"email": user.email})
    if reset_form.is_valid():
        reset_form.save(email_template_name=_get_email_template_name_for_reset_password(language_code))


def _get_email_template_name_for_reset_password(language):
    return 'registration/password_reset_email_' + unicode(language) + '.html'


def convert_dmy_to_ymd(str_date):
    date = datetime.strptime(str_date, "%d-%m-%Y")
    return datetime.strftime(date, "%Y-%m-%d")


def get_changed_questions(olds, news, subject=True):
    i_old = 0
    deleted = []
    added = []
    changed = []
    changed_type = []
    if subject:
        if olds[-1].label != news[-1].label:
            changed.append(news[-1].label)
        olds = olds[:-1]
        news = news[:-1]
    for i_new, new in enumerate(news):
        while True:
            try:
                if new.name == olds[i_old].name:
                    if new.label != olds[i_old].label:
                        changed.append(new.label)
                    elif new.type != olds[i_old].type:
                        changed_type.append(dict({"label": new.label, "type": new.type}))
                    i_old += 1
                    break
                deleted.append(olds[i_old].label)
                i_old += 1
            except IndexError:
                added.append(new.label)
                break

    if i_old < len(olds):
        for key, old in enumerate(olds[i_old:]):
            deleted.append(old.label)

    all_type_dict = dict(changed=changed, changed_type=changed_type, added=added, deleted=deleted)
    return_dict = dict()
    for type, value in all_type_dict.items():
        if len(value):
            return_dict.update({type: value})
    return return_dict


def generate_project_name(project_names):
    default_name = _("Untitled Project")
    current_project = unicode(default_name)
    i = 1
    while current_project.lower() in project_names:
        current_project = u"%s - %d" % (default_name, i)
        i += 1
    return current_project


def _get_email_template_name_for_created_user(language):
    return 'registration/created_user_email_' + unicode(language) + '.html'

def translate(message, language="en", func=_):
    current_language = get_language()
    activate(language)
    translated = func(message)
    activate(current_language)
    return translated


def get_text_language_by_instruction(instruction):
    if re.match(r'^La r.ponse doit.+$', instruction):
        return "fr"
    return "en"

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def get_map_key(host):
    try:
        return settings.API_KEYS.get(host)
    except :
        return ""

def random_string(length=6):
    return ''.join(random.sample('abcdefghijklmnopqrs', length))


def is_empty_string(value):
    return value is None or value.strip() == ''
