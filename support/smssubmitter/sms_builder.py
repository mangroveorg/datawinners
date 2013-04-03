from src.read import ReadConfig
from random import choice
from numpy.lib.utils import safe_eval
from multiprocessing import Process
from selenium import webdriver

class SMSBuilder:

    function_map = {'word':"get_word_answer", "gps":"get_gps_answer", "choice":"get_choice_answer", "date":"get_date_answer","number":"get_number_answer"}

    def get_word_answer(self):
        return choice(safe_eval(ReadConfig().get_word_data))

    def get_gps_answer(self):
        return choice(safe_eval(ReadConfig().get_gps_data))+","+choice(safe_eval(ReadConfig().get_gps_data))

    def get_choice_answer(self):
        return choice(safe_eval(ReadConfig().get_choice_data))

    def get_date_answer(self):
        return choice(safe_eval(ReadConfig().get_date_data))

    def get_number_answer(self):
        return choice(safe_eval(ReadConfig().get_number_data))

    def get_subject(self):
        return choice(safe_eval(ReadConfig().get_subject_data))

    def get_activity_period(self):
        return ReadConfig().get_activity_period

    def get_qcode(self):
        return ReadConfig().get_questionnaire_code

    def get_sms_answer(self):
        answers = ""
        question_order = eval(ReadConfig().get_question_order)
        key_list = sorted(question_order.keys())
        for key in key_list:
            func_name = str(self.function_map.get(question_order.get(key)))
            answers = answers + str ( getattr(self, func_name)() ) + " "
        return answers

    def get_sms_submission(self):
        return self.get_qcode()+" "+self.get_subject()+ " " + self.get_activity_period() + " " +  self.get_sms_answer()


class  SMSSubmission:

    TO_NUM_LOC=safe_eval(ReadConfig().get_to_num_locator)
    FROM_NUM_LOC=safe_eval(ReadConfig().get_from_num_locator)
    SMS_MESSAGE_LOC=safe_eval(ReadConfig().get_sms_message_locator)
    SEND_SMS_LOC=safe_eval(ReadConfig().get_send_sms_button_locator)

    def multiple_submit_sms(self,pn,driver):

        print "Thread:" + str(pn) +"started."

        for num in range(safe_eval(ReadConfig().get_num_submissions_per_process)):
            driver.get("http://"+safe_eval(ReadConfig().get_ip_address)+"/smstester")
            to_number_ele=driver.find_element_by_css_selector(self.TO_NUM_LOC)
            from_number_ele=driver.find_element_by_css_selector(self.FROM_NUM_LOC)
            sms_ele=driver.find_element_by_css_selector  (self.SMS_MESSAGE_LOC)
            sms_send_btn=driver.find_element_by_css_selector(self.SEND_SMS_LOC)
            to_number_ele.clear()
            to_number_ele.send_keys(safe_eval(ReadConfig().get_to_num_data))
            from_number_ele.clear()
            from_number_ele.send_keys(safe_eval(ReadConfig().get_from_num_data))

            sms_ele.clear()
            sms_ele.send_keys(SMSBuilder().get_sms_submission())
            sms_send_btn.click()

        print "Thread:" + str(pn) +"ended."

if __name__== "__main__" :

    num_procs=safe_eval(ReadConfig().get_num_procs)
    for num in range(num_procs):
        Process(target=SMSSubmission().multiple_submit_sms,args=(num,webdriver.Firefox())).start()
