from datawinners.accountmanagement.models import NGOUserProfile

def ngo_user_created(sender, user, request, **kwargs):
    data = NGOUserProfile()
    data.org_id = kwargs['organization_id']
    data.title = kwargs['title']
    data.user=user
    print 'saving the user'
    data.save()

from registration.signals import user_registered
user_registered.connect(ngo_user_created)