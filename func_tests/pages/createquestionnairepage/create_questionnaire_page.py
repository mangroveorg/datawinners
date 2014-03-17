# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from selenium.webdriver.support.select import Select

from framework.utils.data_fetcher import *
from framework.utils.global_constant import WAIT_FOR_TITLE
from pages.createdatasenderquestionnairepage.create_data_sender_questionnaire_page import CreateDataSenderQuestionnairePage
from pages.createprojectpage.create_project_locator import PROJECT_NAME_TB, SAVE_AND_CREATE_BTN, INFORM_DATASENDERS_OK_BUTTON_BY_CSS
from pages.createquestionnairepage.create_questionnaire_locator import *
from pages.projectoverviewpage.project_overview_page import ProjectOverviewPage
from pages.warningdialog.questionnaire_modified_dialog import QuestionnaireModifiedDialog
from tests.projects.questionnairetests.project_questionnaire_data import *
from framework.utils.common_utils import generateId, CommonUtilities
from selenium.common.exceptions import NoSuchElementException
from tests.testsettings import UI_TEST_TIMEOUT
from pages.page import Page

MANDATORY_FIELD_ERROR_MESSAGE = "This field is required."

class CreateQuestionnairePage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)
        self.SELECT_FUNC = {
                                WORD: self.configure_word_type_question,
                                NUMBER: self.configure_number_type_question,
                                DATE: self.configure_date_type_question,
                                LIST_OF_CHOICES: self.configure_list_of_choices_type_question,
                                GEO: self.configure_geo_type_question
                            }

    def create_questionnaire_with(self, project_data, questionnaire_data):
        """
        Function to create a questionnaire on the 'create questionnaire' page

        Args:
        questionnaire_data is data to fill in the different fields of the questionnaire page

        Return self
        """
        self.type_project_name(project_data)
        questionnaire_code = fetch_(QUESTIONNAIRE_CODE, from_(questionnaire_data))
        gen_ramdom = fetch_(GEN_RANDOM, from_(questionnaire_data))
        if gen_ramdom:
            questionnaire_code = questionnaire_code + generateId()
        if fetch_(QUESTIONNAIRE_CODE, from_(questionnaire_data)):
            self.driver.find_text_box(QUESTIONNAIRE_CODE_TB).enter_text(questionnaire_code)
        for question in fetch_(QUESTIONS, from_(questionnaire_data)):
            self.add_question(question)
        return self

    def type_project_name(self, project_data):
        project_name = fetch_(PROJECT_NAME, from_(project_data))
        try:
            gen_random = fetch_(GEN_RANDOM, from_(project_data))
        except KeyError:
            gen_random = False
        if gen_random:
            project_name += generateId()
        self.driver.find_text_box(PROJECT_NAME_TB).enter_text(project_name)
        return project_name

    def create_questionnaire_to_work_performed_subjects_with(self, questionnaire_data):
        """
        Function to create a questionnaire on the 'create questionnaire' page

        Args:
        questionnaire_data is data to fill in the different fields of the questionnaire page

        Return self
        """
        questionnaire_code = fetch_(QUESTIONNAIRE_CODE, from_(questionnaire_data))
        gen_ramdom = fetch_(GEN_RANDOM, from_(questionnaire_data))
        if gen_ramdom:
            questionnaire_code = questionnaire_code + generateId()
        self.driver.find_text_box(QUESTIONNAIRE_CODE_TB).enter_text(questionnaire_code)
        for question in fetch_(QUESTIONS, from_(questionnaire_data)):
            self.add_question(question)
        return self

    def add_question(self, question):
        self.click_add_question_link()
        self.fill_question_title(question)
        self.SELECT_FUNC[fetch_(TYPE, from_(question))](question)

    def save_questionnaire_successfully(self):
        """
        Function to save the questionnaire page successfully

        return self
        """
        self.driver.find(SAVE_CHANGES_BTN).click()
        self.driver.wait_for_page_with_title(WAIT_FOR_TITLE, "Data Senders")
        return CreateDataSenderQuestionnairePage(self.driver)

    def save_questionnaire(self):
        """
        Function to save the questionnaire page

        return self
        """
        self.driver.find(SAVE_CHANGES_BTN).click()
        return self

    def create_default_question(self, question_data, question_link):
        """
        Function to define a default question on the questionnaire page

        Args:
        question_data is data to create a default entity question
        question_link is the locator for default question

        return self
        """
        self.driver.find(question_link).click()
        self.fill_question_title(question_data)
        return self


    def fill_question_title(self, question_data):
        """
        Function to fill the question and code text box on the questionnaire page

        Args:
        question_data is data to fill in the question and code text boxes

        return self
        """
        self.driver.find_text_box(QUESTION_TB).enter_text(fetch_(QUESTION, from_(question_data)))
        return self


    def configure_word_type_question(self, question_data):
        """
        Function to select word or phrase option and fill the details (min or max) on the questionnaire page

        Args:
        question_data is data to fill in the min and max fields

        return self
        """
        self.driver.find_drop_down(ANSWER_TYPE_DROPDOWN).set_selected(WORD_OR_PHRASE)
        limit = fetch_(LIMIT, from_(question_data))
        if limit == LIMITED:
            self.driver.find_radio_button(CHARACTER_LIMIT_RB).click()
            self.driver.find_text_box(WORD_OR_PHRASE_MAX_LENGTH_TB).enter_text(fetch_(MAX, from_(question_data)))
        elif limit == NO_LIMIT:
            self.driver.find_radio_button(NO_CHARACTER_LIMIT_RB).click()
        return self


    def configure_number_type_question(self, question_data):
        """
        Function to select number option and fill the details (min or max) on the questionnaire page

        Args:
        question_data is data to fill in the min and max fields

        return self
        """
        self.driver.find_drop_down(ANSWER_TYPE_DROPDOWN).set_selected(NUMBER_OPTION)
        self.driver.find_text_box(NUMBER_MIN_LENGTH_TB).enter_text(fetch_(MIN, from_(question_data)))
        self.driver.find_text_box(NUMBER_MAX_LENGTH_TB).enter_text(fetch_(MAX, from_(question_data)))
        return self


    def configure_date_type_question(self, question_data):
        """
        Function to select date option and date format on the questionnaire page

        Args:
        question_data is data to select date type

        return self
        """
        self.driver.find_drop_down(ANSWER_TYPE_DROPDOWN).set_selected(DATE_OPTION)
        date_format = fetch_(DATE_FORMAT, from_(question_data))
        if (date_format == MM_YYYY):
            self.driver.find_radio_button(MONTH_YEAR_RB).click()
        elif (date_format == DD_MM_YYYY):
            self.driver.find_radio_button(DATE_MONTH_YEAR_RB).click()
        elif (date_format == MM_DD_YYYY):
            self.driver.find_radio_button(MONTH_DATE_YEAR_RB).click()
        return self


    def configure_list_of_choices_type_question(self, question_data):
        """
        Function to select list of choices option and add the choices on the questionnaire page

        Args:
        question_data is to add the choices on the page

        return self
        """
        self.driver.find_drop_down(ANSWER_TYPE_DROPDOWN).set_selected(LIST_OF_CHOICES_OPTION)
        self.driver.find_element_by_id("choice_text0").clear()
        index = 1
        choices = fetch_(CHOICE, from_(question_data))
        for choice in choices:
            if index > 1:
                self.driver.find(ADD_CHOICE_LINK).click()
                box = self.driver.find_text_box(by_id("choice_text%d" % (index-1)))
                box.send_keys(choice)
            index += 1
        box = self.driver.find_text_box(by_xpath(CHOICE_XPATH_LOCATOR + "[1]" + CHOICE_TB_XPATH_LOCATOR))
        box.send_keys(choices[0])
        choice_type = fetch_(ALLOWED_CHOICE, from_(question_data))
        if ONLY_ONE_ANSWER == choice_type:
            self.driver.find_radio_button(ONLY_ONE_ANSWER_RB).click()
        elif MULTIPLE_ANSWERS == choice_type:
            self.driver.find_radio_button(MULTIPLE_ANSWER_RB).click()
        return self


    def configure_geo_type_question(self, question_data):
        """
        Function to select geo option on the questionnaire page

        Args:
        question_data is data to select geo type

        return self
        """
        self.driver.find_drop_down(ANSWER_TYPE_DROPDOWN).set_selected(GPS_COORDINATES)
        return self


    def get_success_message(self):
        """
        Function to fetch the success message from label of the questionnaire page

        Return success message
        """
        comm_utils = CommonUtilities(self.driver)
        if comm_utils.wait_for_element(10, SUCCESS_MESSAGE_LABEL):
            return self.driver.find(SUCCESS_MESSAGE_LABEL).text
        else:
            return "Success message not appeared on the page."


    def get_remaining_character_count(self):
        """
        Function to fetch the remaining character count from label of the questionnaire page

        Return success message
        """
        return self.driver.find(CHARACTER_COUNT).text


    def get_question_link_text(self, question_number):
        """
        Function to get the text of the question link

        Args:
        question_number is index number of the question

        Return link text
        """
        question_locator = QUESTION_LINK_CSS_LOCATOR_PART1 + ":nth-child(" + str(
            question_number) + ")" + QUESTION_LINK_CSS_LOCATOR_PART2
        return self.driver.find(by_css(question_locator)).text

    def get_last_question_link_text(self):
        return self.driver.find(LAST_QUESTION_LINK_LOCATOR).text

    def select_question_link(self, question_number):
        """
        Function to select the question link

        Args:
        question_number is index number of the question
        """
        question_locator = QUESTION_LINK_CSS_LOCATOR_PART1 + ":nth-child(" + str(
            question_number) + ")" + QUESTION_LINK_CSS_LOCATOR_PART2
        self.driver.find(by_css(question_locator)).click()


    def get_question(self):
        """
        Function to fetch the question text on the questionnaire page

        return question
        """
        return self.driver.find_text_box(QUESTION_TB).get_attribute("value")


    def get_question_code(self):
        """
        Function to fetch the question text on the questionnaire page

        return question_code
        """
        return self.driver.find_text_box(CODE_TB).get_attribute("value")

    def get_select_or_edit_question_message(self):

        return self.driver.find_element_by_css_selector(".select_question_message")


    def navigate_to_previous_step(self):
        """
        Function to go on subject questionnaire page

        Return self
        """
        self.driver.find(PREVIOUS_STEP_LINK).click()
        from pages.createsubjectquestionnairepage.create_subject_questionnaire_page import CreateSubjectQuestionnairePage

        return CreateSubjectQuestionnairePage(self.driver)


    def get_page_title(self):
        try:
            return self.driver.find_element_by_css_selector('.project_title').text
        except NoSuchElementException:
            return ""


    def get_word_type_question(self):
        """
        Function to get the word or phrase option and the details of max on the questionnaire page

        return question dict
        """
        question = dict()
        if self.driver.find_drop_down(ANSWER_TYPE_DROPDOWN).is_selected(WORD_OR_PHRASE):
            question[TYPE] = WORD
        if self.driver.find_radio_button(CHARACTER_LIMIT_RB).is_selected():
            question[LIMIT] = LIMITED
            question[MAX] = self.driver.find_text_box(WORD_OR_PHRASE_MAX_LENGTH_TB).get_attribute("value")
        elif self.driver.find_radio_button(NO_CHARACTER_LIMIT_RB).is_selected():
            question[LIMIT] = NO_LIMIT
        question[QUESTION] = self.get_question()
        question[CODE] = self.get_question_code()
        return question


    def get_number_type_question(self):
        """
        Function to get the number option and the details min or max on the questionnaire page

        return question dict
        """
        question = dict()
        if self.driver.find_drop_down(ANSWER_TYPE_DROPDOWN).is_selected(NUMBER_OPTION):
            question[TYPE] = NUMBER
        question[MIN] = self.driver.find_text_box(NUMBER_MIN_LENGTH_TB).get_attribute("value")
        question[MAX] = self.driver.find_text_box(NUMBER_MAX_LENGTH_TB).get_attribute("value")
        question[QUESTION] = self.get_question()
        question[CODE] = self.get_question_code()
        return question


    def get_date_type_question(self):
        """
        Function to get date type question option and date format on the questionnaire page

        return question dict
        """
        question = dict()
        if self.driver.find_drop_down(ANSWER_TYPE_DROPDOWN).is_selected(DATE_OPTION):
            question[TYPE] = DATE
        if self.driver.find_radio_button(MONTH_YEAR_RB).is_selected():
            question[DATE_FORMAT] = MM_YYYY
        elif self.driver.find_radio_button(DATE_MONTH_YEAR_RB).is_selected():
            question[DATE_FORMAT] = DD_MM_YYYY
        elif self.driver.find_radio_button(MONTH_DATE_YEAR_RB).is_selected():
            question[DATE_FORMAT] = MM_DD_YYYY
        question[QUESTION] = self.get_question()
        question[CODE] = self.get_question_code()
        return question


    def get_list_of_choices_type_question(self):
        """
        Function to get the list of choices question option on the questionnaire page

        return question dict
        """
        question = dict()
        if self.driver.find_drop_down(ANSWER_TYPE_DROPDOWN).is_selected(LIST_OF_CHOICES_OPTION):
            question[TYPE] = LIST_OF_CHOICES
            #options_tbs = self.driver.find_elements_(by_xpath(CHOICE_XPATH_LOCATOR))
        options_tbs = self.driver.find_elements_(by_xpath(CHOICE_XPATH_LOCATOR + CHOICE_TB_XPATH_LOCATOR))
        count = options_tbs.__len__() + 1
        choices = []
        index = 1
        for options_tb in options_tbs:
        #while index < count:
            #choices.append(self.driver.find_text_box(by_xpath(CHOICE_XPATH_LOCATOR + "[" + str(index) + "]" + CHOICE_TB_XPATH_LOCATOR)).get_attribute("value"))
            #index = index + 1
            choices.append(options_tb.get_attribute("value"))
        question[CHOICE] = choices

        if self.driver.find_radio_button(ONLY_ONE_ANSWER_RB).is_selected():
            question[ALLOWED_CHOICE] = ONLY_ONE_ANSWER
        elif self.driver.find_radio_button(MULTIPLE_ANSWER_RB).is_selected():
            question[ALLOWED_CHOICE] = MULTIPLE_ANSWERS

        question[QUESTION] = self.get_question()
        question[CODE] = self.get_question_code()
        return question


    def get_geo_type_question(self):
        """
        Function to get the geo type question options on the questionnaire page

        return question dict
        """
        question = dict()
        if self.driver.find_drop_down(ANSWER_TYPE_DROPDOWN).is_selected(GPS_COORDINATES):
            question[TYPE] = GEO
        question[QUESTION] = self.get_question()
        question[CODE] = self.get_question_code()
        return question

    def go_back(self):
        self.driver.find(BACK_LINK).click()

    def get_questionnaire_code(self):
        return self.driver.find_text_box(QUESTIONNAIRE_CODE_TB).get_attribute("value")

    def get_questionnaire_title(self):
        return self.driver.find_text_box(by_id("questionnaire_title")).get_attribute("value")

    def get_option_by_index_for_multiple_choice_question(self, index):
        code = self.driver.find(by_xpath(CHOICE_XPATH_LOCATOR + "[" + str(index) + "]" + CHOICE_S_XPATH_LOCATOR)).text
        text = self.driver.find_text_box(
            by_xpath(CHOICE_XPATH_LOCATOR + "[" + str(index) + "]" + CHOICE_TB_XPATH_LOCATOR)).get_attribute("value")
        return {'code': code, 'text': text}

    def delete_option_for_multiple_choice_question(self, index):
        self.driver.find(by_id("delete_choice%d" % (index-1))).click()


    def change_date_type_question(self, date_format):
        if date_format == MM_YYYY:
            self.driver.find_radio_button(MONTH_YEAR_RB).click()
        elif date_format == DD_MM_YYYY:
            self.driver.find_radio_button(DATE_MONTH_YEAR_RB).click()
        elif date_format == MM_DD_YYYY:
            self.driver.find_radio_button(MONTH_DATE_YEAR_RB).click()
        return self

    def change_question_text(self, index, new_text):
        """
        Function change a text of one question

        """
        question_locator = QUESTION_LINK_CSS_LOCATOR_PART1 + ":nth-child(" + str(
            index) + ")" + QUESTION_LINK_CSS_LOCATOR_PART2
        self.driver.find(by_css(question_locator)).click()
        return self.driver.find_text_box(QUESTION_TB).enter_text(new_text)

    def period_question_tip_is_displayed(self):
        return self.driver.find(by_css(PERIOD_QUESTION_TIP_CSS_LOCATOR)).is_displayed()

    def click_add_question_link(self):
        self.driver.find(ADD_A_QUESTION_LINK).click()

    def delete_question(self, index):
        """
        Function change a text of one question

        """
        self.driver.find_elements_(by_css(".questions li"))[index-1].click()
        self.driver.find_elements_(by_css(".questions li .delete_link"))[index-1].click()

    def get_question_type(self, index):
        question_locator = QUESTION_LINK_CSS_LOCATOR_PART1 + ":nth-child(" + str(
            index) + ")" + QUESTION_LINK_CSS_LOCATOR_PART2
        self.driver.find(by_css(question_locator)).click()
        return self.driver.find(CURRENT_QUESTION_TYPE_LOCATOR).get_attribute("value")

    def get_nth_option_of_choice(self, index):
        return self.driver.find(by_id("choice_text%d" % (index-1)))

    def change_nth_option_of_choice(self, index, new_text):
        self.driver.find_text_box(by_id("choice_text%d" % (index-1))).enter_text(new_text)

    def change_number_question_limit(self, max_value, min_value=0):
        self.set_min_range_limit(min_value)
        self.set_max_range_limit(max_value)

    def set_min_range_limit(self, limit):
        self.driver.find_text_box(NUMBER_MIN_LENGTH_TB).enter_text(limit)

    def set_max_range_limit(self, limit):
        self.driver.find_text_box(NUMBER_MAX_LENGTH_TB).enter_text(limit)

    def set_word_question_max_length(self, max_length):
        self.driver.find_radio_button(CHARACTER_LIMIT_RB).click()
        self.driver.find_text_box(WORD_OR_PHRASE_MAX_LENGTH_TB).enter_text(max_length)

    def set_questionnaire_code(self, form_code):
        self.driver.find_text_box(QUESTIONNAIRE_CODE_TB).enter_text(form_code)

    def add_option_to_a_multiple_choice_question(self, new_choice_text):
        self.driver.find(by_id("add_choice")).click()
        question = self.get_list_of_choices_type_question()
        index = len(question[CHOICE])
        self.driver.find_text_box(
            by_xpath(CHOICE_XPATH_LOCATOR + "[" + str(index) + "]" + CHOICE_TB_XPATH_LOCATOR)).enter_text(
            new_choice_text)

    def change_list_of_choice_answer_type(self, choice_type):
        if ONLY_ONE_ANSWER == choice_type:
            self.driver.find_radio_button(ONLY_ONE_ANSWER_RB).click()
        elif MULTIPLE_ANSWERS == choice_type:
            self.driver.find_radio_button(MULTIPLE_ANSWER_RB).click()

    def got_redistribute_questionnaire_message(self):
        comm_utils = CommonUtilities(self.driver)
        locator = comm_utils.is_element_present(INFORM_DATASENDERS_OK_BUTTON_BY_CSS)
        if locator and locator.is_displayed():
            locator.click()

    def save_and_create_project_successfully(self, click_ok=True):
        self.driver.find(SAVE_AND_CREATE_BTN).click()
        self.driver.wait_for_page_with_title(UI_TEST_TIMEOUT, "Questionnaires - Overview")
        if click_ok:
            self.got_redistribute_questionnaire_message()
        return ProjectOverviewPage(self.driver)

    def submit_errored_questionnaire(self):
        self.driver.find(SAVE_AND_CREATE_BTN).click()

    def save_and_create_project(self, click_ok=True):
        self.driver.find(SAVE_AND_CREATE_BTN).click()
        if click_ok:
            self.got_redistribute_questionnaire_message()
        return self

    def change_question_type(self, question):
        self.SELECT_FUNC[fetch_(TYPE, from_(question))](question)

    def set_questionnaire_title(self, title, generate_random=False):
        questionnaire_title = title + generateId() if generate_random else title
        self.driver.find_text_box(by_id("questionnaire_title")).enter_text(questionnaire_title)
        return questionnaire_title

    def set_question_title(self, title):
        self.driver.find_text_box(by_id("question_title")).enter_text(title)

    def add_choice_option_to_selected_question(self, choice_text=None):
        self.driver.find(by_id("add_choice")).click()
        if choice_text:
            self.driver.find_text_box(by_css("#options_list input:last")).enter_text(choice_text)

    def is_empty_submission_popup_present(self):
        popup = self.driver.find_element_by_xpath(".//*[@id='no_questions_exists']")
        return popup.is_displayed()

    def _get_validation_message_for(self, questionnaire_field_id):
        try:
            question_title_validation_message = self.driver.find_element_by_id(questionnaire_field_id)
            return question_title_validation_message.is_displayed(), question_title_validation_message.text
        except NoSuchElementException:
            return False, ""


    def get_existing_questions_count(self):
        return len(self.driver.find_elements_(by_css("#qns_list li")))

    def get_max_length_error_message(self):
        return self._get_validation_message_for("max_length_validation_message")

    def get_min_range_error_message(self):
        return self._get_validation_message_for("min_range_validation_message")

    def get_max_range_error_message(self):
        return self._get_validation_message_for("max_range_validation_message")

    def get_questionnaire_title_error_message(self):
        return self._get_validation_message_for("questionnaire_title_validation_message")

    def get_questionnaire_code_error_message(self):
        return self._get_validation_message_for("questionnaire_code_validation_message")

    def get_choice_error_message(self, index):
        return self._get_validation_message_for("choice_validation_message%d" % (index-1))

    def get_duplicate_questionnaire_code_error_message(self):
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_css("#project-message-label .error_message"))
        return self.driver.find_element_by_css_selector("#project-message-label .error_message").text

    def get_questionnaire_language(self):
        return Select(self.driver.find(by_name("project_language"))).first_selected_option.text

    def set_questionnaire_language(self, language):
        Select(self.driver.find(by_name("project_language"))).select_by_visible_text(language)

    def get_existing_questions(self):
        questions = []
        questions_divs = self.driver.find_elements_(by_css('#qns_list>ol>li>a'))
        for q in questions_divs:
            questions.append(q.text)
        return questions

    def back_to_questionnaire_creation_page(self):
        from pages.createprojectpage.questionnaire_creation_options_page import QuestionnaireCreationOptionsPage
        self.driver.find_element_by_id("back_to_create_options").click()
        QuestionnaireModifiedDialog(self.driver).ignore_changes()
        self.driver.wait_for_element(UI_TEST_TIMEOUT, by_xpath(".//*[@id='project_profile']/h5"), True)
        return QuestionnaireCreationOptionsPage(self.driver)