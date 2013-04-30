from mangrove.datastore.documents import SurveyResponseDocument
from mangrove.feeds.documents import SurveyEventDocument
from mangrove.form_model.field import TextField, IntegerField, SelectField
from mangrove.form_model.validation import TextLengthConstraint, NumericRangeConstraint
from mangrove.bootstrap import initializer
from mangrove.datastore.entity import create_entity
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.database import get_db_manager, _delete_db_and_remove_db_manager
from mangrove.datastore.entity_type import define_type
from mangrove.feeds.events import create_event
from mangrove.transport.contract.response import Response
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from mangrove.form_model.form_model import FormModel, NAME_FIELD, MOBILE_NUMBER_FIELD
from mangrove.transport.player.integrationtests.test_sms_submission import LocationTree
from mangrove.transport.player.new_players import SMSPlayerV2
from mangrove.transport.player.player import SMSPlayer
from datawinners.project.models import Project, ProjectState
from datawinners.main.utils import sync_views as datawinners_sync_views

FORM_CODE = 'events_test'

class TestEventCreation(MangroveTestCase):
    def setUp(self):
        MangroveTestCase.setUp(self)
        self.events_manger = get_db_manager('http://localhost:5984/', 'feed-mangrove-test')
        _delete_db_and_remove_db_manager(self.events_manger)
        self.events_manger = get_db_manager('http://localhost:5984/', 'feed-mangrove-test')
        initializer.run(self.manager)
        datawinners_sync_views(self.manager)
        define_type(self.manager, ["dog"])
        self.entity_type = ["healthfacility", "clinic"]
        define_type(self.manager, self.entity_type)
        self.name_type = DataDictType(self.manager, name='Name', slug='name', primitive_type='string')
        self.telephone_number_type = DataDictType(self.manager, name='telephone_number', slug='telephone_number',
            primitive_type='string')
        self.entity_id_type = DataDictType(self.manager, name='Entity Id Type', slug='entity_id',
            primitive_type='string')
        self.stock_type = DataDictType(self.manager, name='Stock Type', slug='stock', primitive_type='integer')
        self.color_type = DataDictType(self.manager, name='Color Type', slug='color', primitive_type='string')

        self.name_type.save()
        self.telephone_number_type.save()
        self.stock_type.save()
        self.color_type.save()

        self.entity = create_entity(self.manager, entity_type=self.entity_type,
            location=["India", "Pune"], aggregation_paths=None, short_code="cli1",
        )
        self.entity.add_data(data=[('name', 'somename', self.name_type)])

        self.data_record_id = self.entity.add_data(data=[("Name", "Ruby", self.name_type)],
            submission=dict(submission_id="1"))

        self.reporter = create_entity(self.manager, entity_type=["reporter"],
            location=["India", "Pune"], aggregation_paths=None, short_code="rep1",
        )

        self.reporter.add_data(data=[(MOBILE_NUMBER_FIELD, '1234', self.telephone_number_type),
                                     (NAME_FIELD, "Test_reporter", self.name_type)], submission=dict(submission_id="2"))

        question1 = TextField(name="entity_question", code="EID", label="What is associated entity",
            entity_question_flag=True, ddtype=self.entity_id_type)
        question2 = TextField(name="Name", code="NAME", label="Clinic Name",
            defaultValue="some default value",
            constraints=[TextLengthConstraint(4, 15)],
            ddtype=self.name_type, required=False)
        question3 = IntegerField(name="Arv stock", code="ARV", label="ARV Stock",
            constraints=[NumericRangeConstraint(min=15, max=120)], ddtype=self.stock_type, required=False)
        question4 = SelectField(name="Color", code="COL", label="Color",
            options=[("RED", 1), ("YELLOW", 2)], ddtype=self.color_type, required=False)

        self.form_model = FormModel(self.manager, entity_type=self.entity_type, name="aids", label="Aids form_model",
            form_code="clinic", type='survey', fields=[question1, question2, question3])
        self.form_model.add_field(question4)
        self.form_model__id = self.form_model.save()

        self.project = Project(name="Events Test", project_type="Survey", state=ProjectState.ACTIVE,
            entity_type="clinic")
        self.project.save(self.manager)
        self.submission_handler = None
        self.sms_player = SMSPlayer(self.manager, LocationTree())
        self.sms_player_v2 = SMSPlayerV2(self.manager, [])

    def test_event_create_in_db(self):
        survey_response_id = self.manager._save_document(
            SurveyResponseDocument(channel="transport", source=1234, form_code=FORM_CODE,
                values={'EID': 'cli1', 'NAME': 'soe', 'ARV': '100', 'COL': '1'}, status=True))
        response = Response(None, survey_response_id=survey_response_id, success=True, form_code=FORM_CODE)
        event_id = create_event(response, self.manager, self.events_manger)
        event_document = self.events_manger.get(event_id, SurveyEventDocument)
        self.assertIsNotNone(event_document)
        self.assertEqual(FORM_CODE, event_document.form_code)
        self.assertEqual("success", event_document.status)
        self.assertEqual(survey_response_id, event_document.survey_response_id)
        self.assertEqual({"name": "Events Test", "id": self.project.id, "status": self.project.state},
            event_document.project)
        self.assertEqual(
            {'question': 'What is associated entity', 'answer': 'cli1', 'subject_name': 'somename', 'type': 'subject',
             'question_code': 'EID'}, event_document.values[0])
        self.assertEqual(
            {'question': 'Clinic Name', 'answer': 'soe', 'type': 'string', 'question_code': 'NAME'},
            event_document.values[1])
        self.assertEqual(
            {'question': 'ARV Stock', 'answer': '100', 'type': 'integer',
             'question_code': 'ARV'}, event_document.values[2])
        self.assertEqual(
            {'question': 'Color', 'answer': '1', 'option_value': 'RED', 'type': 'string',
             'question_code': 'COL'}, event_document.values[3])
