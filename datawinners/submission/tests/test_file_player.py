# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os
from unittest import SkipTest
import xlwt
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import IntegerField, TextField
from mock import Mock, patch
from datawinners.entity.import_data import FilePlayer
from mangrove.transport.player.parser import CsvParser, XlsParser
from mangrove.transport import Channel
from datawinners.accountmanagement.models import Organization
from mangrove.utils.entity_builder import EntityBuilder
from mangrove.utils.form_model_builder import FormModelBuilder
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase

UPLOAD_DATA = """
                                FORM_CODE,ID,BEDS,DOCTOR,MEDS
                                clf1,CL001,10,Dr. A,201
                                clf1,CL002,11,Dr. B,202

                                clf2,CL003,12,Dr. C,203
                                clf1,CL004,13,Dr. D,204

                                clf1,CL005,14,Dr. E,205
"""
@SkipTest
class FilePlayerTest(MangroveTestCase):

    def test_should_import_csv_string(self):
        self._build_fixtures()
        with patch("datawinners.utils.get_organization_from_manager") as get_organization:
            organization = Mock(spec=Organization)
            organization.in_trial_mode = True
            get_organization.return_value = organization
            player = FilePlayer(self.manager, CsvParser(), Channel.CSV)

            response = player.accept(UPLOAD_DATA)
            self.assertEqual([True, True, False, True, True], [item.success for item in response])


    def test_should_import_xls_file(self):
        self._init_xls_data()
        self._build_fixtures()
        with patch("datawinners.utils.get_organization_from_manager") as get_organization:
            with patch("datawinners.entity.import_data.get_form_model_by_code") as get_form_model_by_code_mock:
                organization = Mock(spec=Organization)
                organization.in_trial_mode = True
                get_organization.return_value = organization
                get_form_model_by_code_mock.return_value = Mock()
                with open(self.file_name) as f:

                    response = FilePlayer(self.manager, self.parser, Channel.XLS).accept(file_contents=f.read())

                self.assertEqual([True, True, False, True, True], [item.success for item in response])
        self._cleanup_xls_data()

    def _init_xls_data(self):
        self.parser = XlsParser()
        self.file_name = 'test.xls'
        wb = xlwt.Workbook()
        ws = wb.add_sheet('test')
        for row_number, row in enumerate(UPLOAD_DATA.split('\n')):
            for col_number, val in enumerate(row.split(',')):
                ws.write(row_number, col_number, val)
        wb.save(self.file_name)

    def _cleanup_xls_data(self):
        os.remove(self.file_name)


    def _build_fixtures(self):
        entity_type = ["clinic"]
        default_ddtype = DataDictType(self.manager, name='default dd type', slug='string_default',
            primitive_type='string')

        entity_field = TextField('clinic', 'ID', 'clinic label', default_ddtype, entity_question_flag=True)
        beds_field = IntegerField('beds', 'BEDS', 'beds label', default_ddtype)
        doctor_field = TextField('beds', 'DOCTOR', 'doctor label', default_ddtype)
        meds_field = IntegerField('meds', 'MEDS', 'meds label', default_ddtype)

        FormModelBuilder(self.manager, entity_type, 'clf1').add_field(entity_field)\
                                                            .add_field(beds_field)\
                                                            .add_field(doctor_field)\
                                                            .add_field(meds_field)\
                                                            .build()
        [EntityBuilder(self.manager, entity_type, 'cl00%d' % i).build() for i in range(1, 6)]
