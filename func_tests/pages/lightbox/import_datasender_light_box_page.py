# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.lightbox.light_box_locator import *
from pages.page import Page


class ImportDatasenderLightBox(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def get_template_filename(self):
        """
        Return the name of file that will be downloaded when clicking on Use this template link
         """
        file_url = self.driver.find(DOWNLOAD_TEMPLATE_LINK).get_attribute("href")
        return file_url.split("/")[-1]


    def close_light_box(self):
        """
        Function to close the activation light box of a project

        Return create project page
         """
        self.driver.find(CLOSE_BTN).click()
        return self

    def get_message_from_light_box(self):
        """
        Function to fetch the message from light box

        Return message text
         """
        return self.driver.find(MESSAGE_LABEL).text

    def get_title_of_light_box(self):
        """
        Function to fetch the title from light box

        Return title text
         """
        return self.driver.find(TITLE_LABEL).text
