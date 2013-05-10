from unittest import TestCase
from mangrove.datastore.entity import get_by_short_code, Entity
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.transport.contract.submission import Submission
from mangrove.form_model import form_model
from mangrove.datastore.database import get_db_manager
from migration.couch.migrate_subject_short_code_in_submission_values.migrate_subject_short_code_in_submission_values import migrate
import settings


class TestMigrate(TestCase):

    def setUp(self):
        self.database = "hni_testorg_slx364903"
        self.form_code = "cli001"
        self.dbm = get_db_manager(settings.COUCH_DB_SERVER, database=self.database,credentials=settings.COUCHDB_CREDENTIALS)
        self.form = form_model.get_form_model_by_code(self.dbm, self.form_code)
        self.entity_question_code = self.form.entity_question.code
        self.old_short_code, self.new_short_code = self.change_submissions(self.dbm, self.form_code, self.entity_question_code)
        self.change_subject(self.dbm, self.form, self.old_short_code, self.new_short_code)

    def tearDown(self):
        self.change_subject(self.dbm, self.form, self.old_short_code, self.old_short_code)

    def update_submission_values(self, submission, key, value):
        submission.values[key] = value
        submission.save()
        self.id_of_submission_with_wrong_short_code = submission.id

    def get_short_code_in_submission(self, submission, entity_question_code):
        return submission.values[entity_question_code]

    def make_wrong_subject_short_code(self, submission, entity_question_code):
        old_short_code = self.get_short_code_in_submission(submission, entity_question_code)
        new_short_code = old_short_code.upper()
        return old_short_code, new_short_code

    def change_submissions(self, dbm, form_code, entity_question_code):
        submission = self.get_submissions(dbm, form_code, None, None, 0, 1)[0]
        old, new = self.make_wrong_subject_short_code(submission, entity_question_code)
        self.update_submission_values(submission, entity_question_code, new)
        return old, new

    def _get_start_and_end_key(self, form_code, from_time, to_time):
        end = [form_code] if from_time is None else [form_code, from_time]
        start = [form_code, {}] if to_time is None else [form_code, to_time]

        return start, end

    def get_submissions(self, dbm, form_code, from_time, to_time, page_number=0, page_size=None, view_name="submissionlog"):
        startkey, endkey = self._get_start_and_end_key(form_code, from_time, to_time)
        if page_size is None:
            rows = dbm.load_all_rows_in_view(view_name, reduce=False, descending=True,
                startkey=startkey,
                endkey=endkey)
        else:
            rows = dbm.load_all_rows_in_view(view_name, reduce=False, descending=True,
                startkey=startkey,
                endkey=endkey, skip=page_number * page_size, limit=page_size)
        submissions = [Submission.new_from_doc(dbm=dbm, doc=Submission.__document_class__.wrap(row['value'])) for row in
                       rows]
        return submissions

    def update_subject(self, subject, short_code):
        entity_id_field = [field for field in subject.data.values() if field["type"]["name"] == 'Entity Id Type'][0]
        entity_id_field["value"] = short_code
        subject.save()

    def change_subject(self, dbm, form, short_code, new_value):
        subject = get_by_short_code(dbm, short_code, form.entity_type)
        self.update_subject(subject, new_value)

    def test_migrate(self):
        try:
            get_by_short_code(self.dbm, self.new_short_code, self.form.entity_type)
        except DataObjectNotFound as e:
            self.assertIsInstance(e, DataObjectNotFound)

        migrate([self.database])
        submission_after_migration = self.dbm.get(self.id_of_submission_with_wrong_short_code, Submission)

        short_code_migrated_submission = self.get_short_code_in_submission(submission_after_migration, self.entity_question_code)
        self.assertIsInstance(get_by_short_code(self.dbm, short_code_migrated_submission, self.form.entity_type), Entity)

