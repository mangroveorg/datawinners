from django.contrib import admin
from datawinners.feature_toggle.models import Feature, FeatureSubscription
from waffle.models import Flag
from datawinners.accountmanagement.models import NGOUserProfile


class FeatureSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('feature_name', 'organization_names')
    filter_horizontal = ('organizations',)

    def organization_names(self, obj):
        return ', '.join([organization.name for organization in obj.organizations.all()])
#     def organization_id(self, obj):
#         return obj.organization.org_id

    def feature_name(self, obj):
        return obj.feature.name

    feature_name.admin_order_field = "feature__name"

    def save_model(self, request, obj, form, change):
        super(FeatureSubscriptionAdmin, self).save_model(
            request, obj, form, change)

        '''
        #get waffle.flag for feature
            if not exist - create one
            iterate over organization list
                get all users belonging to this organization
                add users to waffle.flag entity users list
                
                - later - on post add / remove of user object, we need to update this list of waffle.flag
        #
        
        '''
        flags = Flag.objects.filter(name=self.feature_name(obj))[:1]
        if flags:
            flag = flags[0]
        else:
            flag = Flag(name=self.feature_name(obj))
            flag.save()
            
        flag.users.clear()    
        user_ids = []
#         reloaded_feature_subscription = FeatureSubscription.objects.get(id=obj.id)
#         org_ids = form.cleaned_data.get('organizations')
        org_ids = [organization.org_id for organization in form.cleaned_data.get('organizations',[])]
#         org_ids = [organization.org_id for organization in reloaded_feature_subscription.organizations.all()]
        for org_id in org_ids:
            user_profiles = NGOUserProfile.objects.filter(org_id=org_id)
            org_user_ids = [user_profile.user_id for user_profile in user_profiles]
            user_ids.extend(org_user_ids)
        for user_id in user_ids:
            flag.users.add(user_id)
                
# class FeatureAdmin(admin.ModelAdmin):
#     list_display = ('name', )

# admin.site.register(Feature, FeatureAdmin)
admin.site.register(Feature)
admin.site.register(FeatureSubscription, FeatureSubscriptionAdmin)
