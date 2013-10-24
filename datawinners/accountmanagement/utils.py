from django.utils.translation import ugettext as _

RELATIVE_DELTA_BY_EMAIL_TYPE = {'three_days_after_activation': ({'days':3}, False),'fifteen_days_after_activation': ({'days':15}, False),
                    'one_month_after_activation': ({'months':1}, False), 'two_months_after_activation': ({'months':2}, False),
                    'four_months_after_activation': ({'months':4}, False), 'six_months_after_activation': ({'months':6}, False),
                    'nine_months_after_activation': ({'months':9}, False), 'eleven_months_after_activation': ({'months':11}, False),
                    'seven_days_before_deactivation': ({'years':1, 'days':-7}, True), 'one_day_before_deactivation': ({'years':1, 'days':-1}, True),
                    'deactivation_day': ({'years':1}, True), 'sixty_days_after_deactivation': ({'years':1, 'days':60}, False)
                    }

def get_email_detail_by_type(email_type):
    mail_dict = {'three_days_after_activation': (_("Get the Most out of Datawinners!"),
                                            "basicaccount/three_days_after_activation", None),
                 'fifteen_days_after_activation': ( _("Find Out What Datawinners Can Do For You!"),
                                              "basicaccount/fifteen_days_after_activation", None),
                 'one_month_after_activation': ( _("Datawinners | We're here to Help!"),
                                              "basicaccount/one_month_after_activation", None),
                 'two_months_after_activation': ( _("Datawinners | Join our Online Community!"),
                                              "basicaccount/two_months_after_activation", None),
                 'four_months_after_activation': ( _("Datawinners | Send Us Your story!"),
                                              "basicaccount/four_months_after_activation", None),
                 'six_months_after_activation': ( _("Datawinners | Just checking in..."),
                                              "basicaccount/six_months_after_activation", None),
                 'nine_months_after_activation': ( _("Datawinners | Why is Data Collection Important to You?"),
                                              "basicaccount/nine_months_after_activation", None),
                 'eleven_months_after_activation': ( _("Datawinners | Share Your Experience!"),
                                               "basicaccount/eleven_months_after_activation", None),
                 'seven_days_before_deactivation': ( _("Your Datawinners Subscription is About to End!"),
                                   "basicaccount/seven_days_before_deactivation", None),
                 'one_day_before_deactivation': ( _("Your Free Subscription to Datawinners Ends Tomorrow - Download Your Data!"),
                            "basicaccount/one_day_before_deactivation", None),
                 'deactivation_day': ( _("Datawinners | Your Account Has Expired!"),
                                       "basicaccount/deactivation_day", None),
                 'sixty_days_after_deactivation': ( _("We'd like to invite You to Back to Datawinners!"),
                                                "basicaccount/sixty_days_after_deactivation", None),
                 'about_to_reach_sms_limit': ( _("DataWinners | 50 SMS Submission Limit Almost Reached: Upgrade to Continue Collecting Data via SMS!"),
                                               "basicaccount/about_to_reach_sms_limit", None),
                 'about_to_reach_submission_limit': ( _("Your DataWinners Submission Limit is Approaching!"),
                                                      "basicaccount/about_to_reach_submission_limit", None),
                 'reached_submission_limit': ( _("DataWinners | Submission Limit Reached: Upgrade to Continue Collecting Data!"),
                                                      "basicaccount/reached_submission_limit", None),
                 }
    return mail_dict[email_type]
  