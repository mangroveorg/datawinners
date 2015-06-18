describe("Create a Poll Questionnaire", function(){

     it('should_validate_poll_questionnaire_title_for_broadcast_option', function(){
         window.smsViewModel = new SmsViewModel();
         window.questionnaireViewModel = new QuestionnaireViewModel();
         var questionnaire_view_model = window.questionnaireViewModel;
         window.pollViewModel = new PollViewModel();
         var poll_questionnaire_model = window.pollViewModel;

         questionnaire_view_model.projectName("");
         poll_questionnaire_model.show_sms("poll_broadcast");
         poll_questionnaire_model.create_poll();
         expect(questionnaire_view_model.projectName.error()).toBe('This field is required');

    });

    it('should_validate_poll_questionnaire_title_for_sms_option', function(){
         window.smsViewModel = new SmsViewModel();
         window.questionnaireViewModel = new QuestionnaireViewModel();
         var questionnaire_view_model = window.questionnaireViewModel;
         window.pollViewModel = new PollViewModel();
         var poll_questionnaire_model = window.pollViewModel;

         questionnaire_view_model.projectName("");
         poll_questionnaire_model.show_sms("poll_via_sms");
         poll_questionnaire_model.create_poll();
         expect(questionnaire_view_model.projectName.error()).toBe('This field is required');

    });

    it('should_not_show_other_option_for_sending_sms_when_poll_is_created', function(){
        window.questionnaireViewModel = new QuestionnaireViewModel();
        var questionnaire_view_model = window.questionnaireViewModel;

        window.smsViewModel = new SmsViewModel();
        var sms_view_model = window.smsViewModel;

        window.pollViewModel = new PollViewModel();
        var poll_questionnaire_model = window.pollViewModel;

        poll_questionnaire_model.show_sms("poll_via_sms");
        poll_questionnaire_model.create_poll();

        expect(smsViewModel.smsOptionList()[0]['label']).toBe('Select Recipients');
        expect(smsViewModel.smsOptionList()[1]['label']).toBe('Group');
        expect(smsViewModel.smsOptionList()[2]['label']).toBe('Contacts linked to a Questionnaire');

    });

    it('should_validate_add_number_of_days', function(){
         var month_name_map = {0:gettext('January') ,
                      1: gettext('February') ,
                      2: gettext('March') ,
                      3: gettext('April') ,
                      4: gettext('May') ,
                      5: gettext('June') ,
                      6: gettext('July') ,
                      7: gettext('August') ,
                      8: gettext('September'),
                      9: gettext('October') ,
                      10:gettext('November') ,
                      11:gettext('December') };

        window.pollViewModel = new PollViewModel();
        var pollViewModel = window.pollViewModel;
        var current_date = new Date();

        pollViewModel.number_of_days(5);
        pollViewModel.from_date_poll(current_date);
        pollViewModel.days_active();
        expected_date = new Date();
        expected_date.setDate(current_date.getDate() + 5);

        expect(pollViewModel.to_date_poll()).toBe(expected_date.getDate()+ " "+ month_name_map[expected_date.getMonth()] +" "+ expected_date.getFullYear())


    });


});