from framework.utils.common_utils import random_number
from testdata.constants import NAME, MOBILE_NUMBER, COMMUNE, EMAIL_ADDRESS, GPS, SUCCESS_MSG

NEW_PASSWORD = "mydstest!123"

VALID_DATASENDER = {
                    NAME: "my_datasender",
                    MOBILE_NUMBER: random_number(9),
                    COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                    GPS: "-21.7622088847 48.0690991394",
                    SUCCESS_MSG: "Registration successful. ID is: rep"
                   }