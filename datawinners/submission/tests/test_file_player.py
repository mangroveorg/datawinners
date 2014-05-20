# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os
import unittest

from django.utils.unittest.case import SkipTest
import xlwt

from mangrove.errors.MangroveException import DataObjectAlreadyExists
from mangrove.form_model.form_model import FormModel, EntityFormModel
from datawinners import utils
from datawinners.tests.data import DEFAULT_TEST_ORG_ID
from mangrove.form_model.field import IntegerField, TextField, ShortCodeField
from mangrove.transport.player.parser import XlsParser
from mangrove.transport import Channel
from mangrove.utils.entity_builder import EntityBuilder
from datawinners.entity.import_data import FilePlayer
from datawinners.accountmanagement.models import Organization


UPLOAD_DATA = """
                                FORM_CODE,BEDS,MEDS,DOCTOR,ID
                                clf12,10,201,Dr. A,CLP001
                                clf12,11,202,Dr. B,CLP002

                                clf12,12, ,Dr. C,CLP003
                                clf12,13,204,Dr. D,CLP004

                                clf12,14,205,Dr. E,CLP005
"""
class FilePlayerTest(unittest.TestCase):
    def setUp(self):
        organization = Organization.objects.get(pk=DEFAULT_TEST_ORG_ID)
        self.manager = utils.get_database_manager_for_org(organization)
    @SkipTest
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
        fields = []
        fields.append(IntegerField('beds', 'BEDS', 'beds label'))
        fields.append(IntegerField('meds', 'MEDS', 'meds label'))
        fields.append(TextField('doctor', 'DOCTOR', 'doctor label'))
        fields.append(ShortCodeField('clinic', 'ID', 'clinic label'))

        try:
            self.form_model = EntityFormModel(self.manager, entity_type=entity_type, name='form_model_name', label='form_model_label',
                                        form_code='clf12', type='form_model_type',  fields=fields, is_registration_model=True)
            form_model_id = self.form_model.save()
            self.form_model = FormModel.get(self.manager, form_model_id)
        except DataObjectAlreadyExists:
            pass

        [EntityBuilder(self.manager, entity_type, 'cl00%d' % i).build().save() for i in range(1, 6)]
