import json
from pages.page import Page
from django.test import Client
from pages.resetpasswordpage.reset_password_page import ResetPasswordPage
from testdata.test_data import url

DS_ACTIVATION_URL = "/datasender/activate/%s-%s"

class DataSenderActivationPage(Page):

    def __init__(self, driver):
        Page.__init__(self, driver)

    def activate_datasender(self, email, password):
        client = Client()
        client.login(username='datawinner', password='d@t@winner')
        r = client.post(path='/admin-apis/datasender/generate_token/', data={'ds_email': email})
        resp = json.loads(r._container[0])
        self.driver.go_to(url(DS_ACTIVATION_URL % (resp["user_id"], resp["token"])))
        activation_page = ResetPasswordPage(self.driver)
        activation_page.type_same_password(password)
        activation_page.click_submit()

        return self
