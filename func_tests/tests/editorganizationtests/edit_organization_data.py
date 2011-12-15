from framework.utils.common_utils import by_css
from testdata.test_data import url

USERNAME = 'username'
PASSWORD = 'password'

VALID_CREDENTIALS = {USERNAME: "tester150411@gmail.com",
                     PASSWORD: "tester150411"}
DATA_WINNERS_ACCOUNT_PAGE = url("/account/")
ORGANIZATION_SECTOR_DROP_DOWN_LIST = by_css("select#id_sector")
