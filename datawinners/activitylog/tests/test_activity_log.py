import unittest
from datetime import datetime, date
from django.contrib.auth.models import User
from mock import Mock, patch
from datawinners.accountmanagement.models import Organization
from django.db.models.base import ModelState

class TestUserActivityLog(unittest.TestCase):
    organization = Mock(spec=Organization)
    organization.org_id = "ABCDXW"
    user = Mock(spec=User)
    user.id = 1
    state = Mock(spec=ModelState)
    state.db = None
    user._state = state
    
    def setUp(self):
        pass

    def test_should_log_activity(self):
        request = Mock()
        request.user = self.user
        with patch("datawinners.utils.get_organization") as get_organization_mock:
            from datawinners.activitylog.models import UserActivityLog
            get_organization_mock.return_value = self.organization
            UserActivityLog().log(request, detail="Nothing", action="Created Project", project="TestCaseProject2Deleted")
            self.matched = UserActivityLog.objects.filter(project="TestCaseProject2Deleted",
                action="Created Project", detail="Nothing")
            inserted = self.matched[0]
            self.assertEquals(len(self.matched), 1)
            self.assertEquals(datetime.strftime(inserted.log_date, "%Y-%m-%d"), datetime.strftime(date.today(), "%Y-%m-%d"))
            self.matched.delete()

    def check_detail_parsing(self, data, expected_detail):
        from datawinners.activitylog.models import UserActivityLog
        log = UserActivityLog(**data)

        self.assertEqual(log.translated_detail(), expected_detail)

    def test_should_return_the_translated_detail_for_project_edition(self):
        edit_project_data = {"project": "untitled", "detail":u'{"deleted": ["added", "new add"]}', "action":"Edited Project"}
        expected = u'Deleted Questions: <ul class="bulleted"><li>added</li><li>new add</li></ul>'
        self.check_detail_parsing(edit_project_data, expected)

        detail = u'{"changed_type": [{"type": "date", "label": "Question 8"}]}'
        edit_registration_form_data = {"project": "untitled", "detail":detail, "action":"Edited Project"}
        self.check_detail_parsing(edit_registration_form_data, u'Answer type changed to date for "Question 8"')

        self.maxDiff = None
        detail = u'{"deleted": ["What is associat\u00e9d entity?", "What is your nam\u00e9?", "What is age \u00f6f father?", "What is r\u00e9porting date?", "What is your blood group?", "What ar\u00e9 symptoms?", "What is the GPS code for clinic?", "Question 8"], "added": ["Which waterpoint are you reporting on?", "What is the reporting period for the activity?", "word", "number", "choices", "gps"], "Name": "minoa", "Language": "mg", "Entity_type": "waterpoint"}'
        edit_registration_form_data = {"project": "untitled", "detail":detail, "action":"Edited Project"}
        expected = u'Name: minoa<br/>Language: mg<br/>Entity_type: waterpoint<br/>Added Questions: <ul class="bulleted"><li>Which waterpoint are you reporting on?</li><li>What is the reporting period for the activity?</li><li>word</li><li>number</li><li>choices</li><li>gps</li></ul><br/>Deleted Questions: <ul class="bulleted"><li>What is associat\xe9d entity?</li><li>What is your nam\xe9?</li><li>What is age \xf6f father?</li><li>What is r\xe9porting date?</li><li>What is your blood group?</li><li>What ar\xe9 symptoms?</li><li>What is the GPS code for clinic?</li><li>Question 8</li></ul>'
        self.check_detail_parsing(edit_registration_form_data, expected)

    def test_should_return_the_translated_detail_for_edit_registration_form(self):
        detail = u'{"deleted": ["What is the clinic\'s mobile telephone number?"], "added": ["new question"], "entity_type": "Clinic"}'
        edit_reg_form_data = {"detail":detail, "action":"Edited Registration Form"}
        expected = u'Subject Type: Clinic<br/>Added Questions: <ul class="bulleted"><li>new question</li></ul><br/>Deleted Questions: <ul class="bulleted"><li>What is the clinic\'s mobile telephone number?</li></ul>'
        self.check_detail_parsing(edit_reg_form_data, expected)
        

    



        


