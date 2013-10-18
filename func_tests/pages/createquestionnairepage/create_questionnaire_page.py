# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from time import sleep

from framework.utils.data_fetcher import *
from framework.utils.global_constant import WAIT_FOR_TITLE
from pages.createdatasenderquestionnairepage.create_data_sender_questionnaire_page import CreateDataSenderQuestionnairePage
from pages.createquestionnairepage.create_questionnaire_locator import *
from tests.projects.questionnairetests.project_questionnaire_data import *
from framework.utils.common_utils import generateId, CommonUtilities
from pages.createprojectpage.create_project_page import CreateProjectPage


class CreateQuestionnairePage(CreateProjectPage):
    def __init__(self, driver):
        CreateProjectPage.__init__(self, driver)
        self.SELECT_FUNC = {WORD: self.configure_word_type_question,
                            NUMBER: self.configure_number_type_question,
                            DATE: self.configure_date_type_question,
                            LIST_OF_CHOICES: self.configure_list_of_choices_type_question,
                            GEO: self.configure_geo_type_question}

    def create_questionnaire_with(self, questionnaire_data):
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
        self.create_default_question(questionnaire_data[DEFAULT_QUESTION], DEFAULT_QUESTION_LINK)
        for question in fetch_(QUESTIONS, from_(questionnaire_data)):
            self.add_question(question)
        return self

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
        self.driver.find(ADD_A_QUESTION_LINK).click()
        self.fill_question_and_code_tb(question)
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
        self.fill_question_and_code_tb(question_data)
        return self


    def fill_question_and_code_tb(self, question_data):
        """
        Function to fill the question and code text box on the questionnaire page

        Args:
        question_data is data to fill in the question and code text boxes

        return self
        """
        self.driver.find_text_box(QUESTION_TB).enter_text(fetch_(QUESTION, from_(question_data)))
        #self.driver.find_text_box(CODE_TB).enter_text(fetch_(CODE, from_(question_data)))
        return self


    def configure_word_type_question(self, question_data):
        """
        Function to select word or phrase option and fill the details (min or max) on the questionnaire page

        Args:
        question_data is data to fill in the min and max fields

        return self
        """
        self.driver.find_radio_button(WORD_OR_PHRASE_RB).click()
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
        self.driver.find_radio_button(NUMBER_RB).click()
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
        self.driver.find_radio_button(DATE_RB).click()
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
        self.driver.find_radio_button(LIST_OF_CHOICE_RB).click()
        self.driver.find_element_by_id("choice_text").clear()
        index = 1
        choices = fetch_(CHOICE, from_(question_data))
        for choice in choices:
            if index > 1:
                self.driver.find(ADD_CHOICE_LINK).click()
                box = self.driver.find_text_box(by_xpath(CHOICE_XPATH_LOCATOR + "[" + str(index) + "]" + CHOICE_TB_XPATH_LOCATOR))
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
        self.driver.find_radio_button(GEO_RB).click()
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


    def navigate_to_previous_step(self):
        """
        Function to go on subject questionnaire page

        Return self
        """
        self.driver.find(PREVIOUS_STEP_LINK).click()
        from pages.createsubjectquestionnairepage.create_subject_questionnaire_page import CreateSubjectQuestionnairePage

        return CreateSubjectQuestionnairePage(self.driver)


    def get_page_title(self):
        """
        Function to return the page title

        Return title
        """
        return "Questionnaire"


    def get_word_type_question(self):
        """
        Function to get the word or phrase option and the details of max on the questionnaire page

        return question dict
        """
        question = dict()
        if self.driver.find_radio_button(WORD_OR_PHRASE_RB).is_selected():
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
        if self.driver.find_radio_button(NUMBER_RB).is_selected():
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
        if self.driver.find_radio_button(DATE_RB).is_selected():
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
        if self.driver.find_radio_button(LIST_OF_CHOICE_RB).is_selected():
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
        if self.driver.find_radio_button(GEO_RB).is_selected():
            question[TYPE] = GEO
        question[QUESTION] = self.get_question()
        question[CODE] = self.get_question_code()
        return question

    def go_back(self):
        self.driver.find(BACK_LINK).click()

    def get_questionnaire_code(self):
        return self.driver.find_text_box(QUESTIONNAIRE_CODE_TB).get_attribute("value")

    def get_option_by_index_for_multiple_choice_question(self, index):
        code = self.driver.find(by_xpath(CHOICE_XPATH_LOCATOR + "[" + str(index) + "]" + CHOICE_S_XPATH_LOCATOR)).text
        text = self.driver.find_text_box(
            by_xpath(CHOICE_XPATH_LOCATOR + "[" + str(index) + "]" + CHOICE_TB_XPATH_LOCATOR)).get_attribute("value")
        return {'code': code, 'text': text}

    def delete_option_for_multiple_choice_question(self, index):
        self.driver.find(by_xpath(CHOICE_XPATH_LOCATOR + "[" + str(index) + "]" + CHOICE_DL_XPATH_LOCATOR)).click()


    def change_date_type_question(self, date_format):
        if (date_format == MM_YYYY):
            self.driver.find_radio_button(MONTH_YEAR_RB).click()
        elif (date_format == DD_MM_YYYY):
            self.driver.find_radio_button(DATE_MONTH_YEAR_RB).click()
        elif (date_format == MM_DD_YYYY):
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
        question_locator = QUESTION_DELETE_LINK_CSS_LOCATOR_PART1 + ":nth-child(" + str(
            index) + ")" + QUESTION_DELETE_LINK_CSS_LOCATOR_PART2
        self.driver.find(by_css(question_locator)).click()

    def change_question_type_to(self, index, type="text"):
        question_locator = QUESTION_LINK_CSS_LOCATOR_PART1 + ":nth-child(" + str(
            index) + ")" + QUESTION_LINK_CSS_LOCATOR_PART2
        self.driver.find(by_css(question_locator)).click()
        self.driver.find(by_css(QUESTION_TYPE_CSS_LOCATOR % str(type))).click()

    def get_question_type(self, index):
        question_locator = QUESTION_LINK_CSS_LOCATOR_PART1 + ":nth-child(" + str(
            index) + ")" + QUESTION_LINK_CSS_LOCATOR_PART2
        self.driver.find(by_css(question_locator)).click()
        return self.driver.find(CURRENT_QUESTION_TYPE_LOCATOR).get_attribute("value")

    def get_nth_option_of_choice(self, index):
        return self.driver.find(by_css('#options_list>li:nth-child(%d)>input' % index))

    def change_nth_option_of_choice(self, index, new_text):
        self.driver.find_text_box(by_css('#options_list>li:nth-child(%d)>input' % index)).enter_text(new_text)

    def change_number_question_limit(self, max_value, min_value=0):
        self.driver.find_text_box(NUMBER_MIN_LENGTH_TB).enter_text(min_value)
        self.driver.find_text_box(NUMBER_MAX_LENGTH_TB).enter_text(max_value)

    def set_word_question_max_length(self, max_length):
        self.driver.find_radio_button(CHARACTER_LIMIT_RB).click()
        self.driver.find_text_box(WORD_OR_PHRASE_MAX_LENGTH_TB).enter_text(max_length)

    def set_questionnaire_code(self, form_code):
        self.driver.find_text_box(QUESTIONNAIRE_CODE_TB).enter_text(form_code)

    def add_option_to_a_multiple_choice_question(self, new_choice_text):
        self.driver.find(ADD_CHOICE_LINK).click()
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
    