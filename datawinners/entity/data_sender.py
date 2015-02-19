from datawinners.accountmanagement.models import NGOUserProfile

def remove_system_datasenders(datasender_list):
    for datasender in datasender_list:
        if datasender["short_code"] == "test":
            index = datasender_list.index(datasender)
            del datasender_list[index]


def get_user_profile_by_reporter_id(reporter_id, user):
    org_id = NGOUserProfile.objects.get(user=user).org_id
    user_profile = NGOUserProfile.objects.filter(reporter_id=reporter_id, org_id=org_id)
    return user_profile[0] if len(user_profile) else None


def get_datasender_user_detail(datasender, user):
    user_profile = get_user_profile_by_reporter_id(datasender['short_code'], user)

    datasender["is_user"] = False
    if user_profile:
        datasender_user_groups = list(user_profile.user.groups.values_list('name', flat=True))
        if "NGO Admins" in datasender_user_groups or "Project Managers" in datasender_user_groups \
            or "Read Only Users" in datasender_user_groups:
            datasender["is_user"] = True
        # datasender['email'] = user_profile.user.email
        # datasender['devices'] = "SMS,Web,Smartphone"
    # else:
    #     datasender['email'] = None
        # datasender['devices'] = "SMS"