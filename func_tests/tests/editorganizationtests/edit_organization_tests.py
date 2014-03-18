from nose.plugins.attrib import attr
from framework.base_test import BaseTest, HeadlessRunnerTest
from tests.endtoendtest.end_to_end_tests import do_login
from tests.editorganizationtests.edit_organization_data import VALID_CREDENTIALS, USERNAME, DATA_WINNERS_ACCOUNT_PAGE, ORGANIZATION_SECTOR_DROP_DOWN_LIST, PASSWORD

class TestEditOrganization(HeadlessRunnerTest):

    @attr('functional_test')
    def test_organization_sector_drop_down_list(self):
        do_login(self.driver, VALID_CREDENTIALS[USERNAME], VALID_CREDENTIALS[PASSWORD])
        self.driver.go_to(DATA_WINNERS_ACCOUNT_PAGE)
        sectors_drop_down = self.driver.find_drop_down(ORGANIZATION_SECTOR_DROP_DOWN_LIST)
        self.assertIn('Please Select', sectors_drop_down.text)
        self.assertIn('Food Security', sectors_drop_down.text)
        self.assertIn('Other', sectors_drop_down.text)