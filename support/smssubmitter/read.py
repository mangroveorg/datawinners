import ConfigParser

class ReadConfig:
    #Need to chnage the path to run on local..
    config_file_path="/Users/vaikuntj/Work/Testing/datawinners/support/smssubmitter/default.conf"

    def __init__(self):
        conf = ConfigParser.SafeConfigParser()
        if len(str(ReadConfig.config_file_path).strip())==0 :
            pass # Need to add an exception class  <Customized Exception classes>
        conf.read(ReadConfig.config_file_path)
        self.conf = conf

    def get(self,section_name, item_name, default_value=None):
        try:
            return self.conf.get(section_name, item_name)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return default_value

    @property
    def get_ip_address(self):
        return self.get("CONF","ip", "datawinnersqa.thoughtworks.com")

    @property
    def get_num_procs(self):
        return self.get("CONF","num_procs", 20)

    @property
    def get_num_submissions_per_process(self):
        return self.get("CONF", "num_submissions_per_process",100)

    @property
    def get_question_order(self):
        return self.get("CONF", "question_order")

    @property
    def get_from_num_locator(self):
        return self.get("LOCATORDATA","FROM_NUM_LOC")

    @property
    def get_to_num_locator(self):
        return self.get("LOCATORDATA","TO_NUM_LOC")

    @property
    def get_sms_message_locator(self):
        return self.get("LOCATORDATA", "SMS_MESSAGE_LOC")

    @property
    def get_send_sms_button_locator(self):
        return self.get("LOCATORDATA", "SEND_SMS_LOC")

    @property
    def get_to_num_data(self):
        return self.get("TEST_DATA", "to_num")

    @property
    def get_from_num_data(self):
        return self.get("TEST_DATA", "from_num")

    @property
    def get_activity_period(self):
        return self.get("TEST_DATA","activity_period")

    @property
    def get_number_data(self):
        return self.get("TEST_DATA","number")

    @property
    def get_word_data(self):
        return self.get("TEST_DATA","word_answer")

    @property
    def get_date_data(self):
        return self.get("TEST_DATA","date_answer")

    @property
    def get_choice_data(self):
        return self.get("TEST_DATA","choice_answer")

    @property
    def get_gps_data(self):
        return self.get("TEST_DATA","gps_answer")

    @property
    def get_subject_data(self):
        return self.get("TEST_DATA","subject")

    @property
    def get_questionnaire_code(self):
        return self.get("TEST_DATA","qcode")
    
    
        
    
    
