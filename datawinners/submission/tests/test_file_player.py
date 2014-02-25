# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os
import unittest
from mangrove.errors.MangroveException import DataObjectAlreadyExists

import xlwt
from datawinners import utils
from datawinners.tests.data import DEFAULT_TEST_ORG_ID
from mangrove.form_model.field import IntegerField, TextField
from mangrove.transport.player.parser import XlsParser
from mangrove.transport import Channel
from mangrove.utils.entity_builder import EntityBuilder
from mangrove.utils.form_model_builder import FormModelBuilder

from datawinners.entity.import_data import FilePlayer
from datawinners.accountmanagement.models import Organization


UPLOAD_DATA = """
                                FORM_CODE,ID,BEDS,DOCTOR,MEDS
                                clf1,CL001,10,Dr. A,201
                                clf1,CL002,11,Dr. B,202

                                clf2,CL003,12,Dr. C
                                clf1,CL004,13,Dr. D,204

                                clf1,CL005,14,Dr. E,205
"""
class FilePlayerTest(unittest.TestCase):
    def setUp(self):
        organization = Organization.objects.get(pk=DEFAULT_TEST_ORG_ID)
        self.manager = utils.get_database_manager_for_org(organization)

    def test_should_import_xls_file(self):
        self._init_xls_data()
        self._build_fixtures()

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

        entity_field = TextField('clinic', 'ID', 'clinic label', entity_question_flag=True)
        beds_field = IntegerField('beds', 'BEDS', 'beds label')
        doctor_field = TextField('beds', 'DOCTOR', 'doctor label')
        meds_field = IntegerField('meds', 'MEDS', 'meds label')
        try:
            FormModelBuilder(self.manager, entity_type, 'clf1').add_field(entity_field)\
                                                            .add_field(beds_field)\
                                                            .add_field(doctor_field)\
                                                            .add_field(meds_field)\
                                                            .build()
        except DataObjectAlreadyExists:
            pass

        [EntityBuilder(self.manager, entity_type, 'cl00%d' % i).build() for i in range(1, 6)]
