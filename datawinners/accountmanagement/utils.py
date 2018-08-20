from django.utils.translation import ugettext as _
from datawinners import settings

RELATIVE_DELTA_BY_EMAIL_TYPE = {'three_days_after_activation':({'days':3}, False),'five_days_after_activation':({'days':5}, False),'seven_days_after_activation':({'days':7}, False),'nine_days_after_activation':({'days':9}, False),'two_months_after_activation': ({'months':2}, False),
                    'four_months_after_activation': ({'months':4}, False), 'six_months_after_activation': ({'months':6}, False),
                    'nine_months_after_activation': ({'months':9}, False), 'eleven_months_after_activation': ({'months':11}, False),
                    'seven_days_before_deactivation': ({'years':1, 'days':-7}, True), 'one_day_before_deactivation': ({'years':1, 'days':-1}, True),
                    'deactivation_day': ({'years':1}, True), 'sixty_days_after_deactivation': ({'years':1, 'days':60}, False)
                    }

PRO_MONTHLY_PRICING = 199
PRO_HALF_YEARLY_PRICING = 149
PRO_YEARLY_PRICING = 99
PRO_SMS_MONTHLY_PRICING = 399
PRO_SMS_HALF_YEARLY_PRICING = 359
PRO_SMS_YEARLY_PRICING = 299

def get_email_detail_by_type(email_type):
    mail_dict = {'three_days_after_activation':("Datawinners | Become a DataWinners Pro in Two Weeks",
                                              "basicaccount/three_days_after_activation", settings.HNI_SUPPORT_EMAIL_ID),
                 'five_days_after_activation':("Datawinners | Authorize your DataWinners Data Senders to Submit Data",
                                              "basicaccount/five_days_after_activation", settings.HNI_SUPPORT_EMAIL_ID),
                 'seven_days_after_activation':("Datawinners | Collect and View Your Data with DataWinners",
                                              "basicaccount/seven_days_after_activation", settings.HNI_SUPPORT_EMAIL_ID),
                 'nine_days_after_activation':("Datawinners | Use Advanced Logic and Collect Media Files with DataWinners",
                                              "basicaccount/nine_days_after_activation", settings.HNI_SUPPORT_EMAIL_ID),
                 'two_months_after_activation': ("Datawinners | Join our Online Community!",
                                              "basicaccount/two_months_after_activation", None),
                 'four_months_after_activation': ("Datawinners | Send Us Your story!",
                                              "basicaccount/four_months_after_activation", None),
                 'six_months_after_activation': ("Datawinners | Just checking in...",
                                              "basicaccount/six_months_after_activation", None),
                 'nine_months_after_activation': ("Datawinners | Why is Data Collection Important to You?",
                                              "basicaccount/nine_months_after_activation", None),
                 'eleven_months_after_activation': ("Datawinners | Share Your Experience!",
                                               "basicaccount/eleven_months_after_activation", None),
                 'seven_days_before_deactivation': ("Your Datawinners Subscription is About to End!",
                                   "basicaccount/seven_days_before_deactivation", settings.HNI_SUPPORT_EMAIL_ID),
                 'one_day_before_deactivation': ("Your Free Subscription to Datawinners Ends Tomorrow - Download Your Data!",
                            "basicaccount/one_day_before_deactivation", settings.HNI_SUPPORT_EMAIL_ID),
                 'deactivation_day': ("Datawinners | Your Account Has Expired!",
                                       "basicaccount/deactivation_day", None),
                 'sixty_days_after_deactivation': ("We'd like to invite You to Back to Datawinners!",
                                                "basicaccount/sixty_days_after_deactivation", settings.HNI_SUPPORT_EMAIL_ID),
                 'about_to_reach_sms_limit': ("DataWinners | 50 SMS Submission Limit Almost Reached: Upgrade to Continue Collecting Data via SMS!",
                                               "basicaccount/about_to_reach_sms_limit", None),
                 'about_to_reach_submission_limit': ("Your DataWinners Submission Limit is Approaching!",
                                                      "basicaccount/about_to_reach_submission_limit", None),
                 'reached_submission_limit': ("DataWinners | Submission Limit Reached: Upgrade to Continue Collecting Data!",
                                                      "basicaccount/reached_submission_limit", None),
                 }
    return mail_dict[email_type]
  