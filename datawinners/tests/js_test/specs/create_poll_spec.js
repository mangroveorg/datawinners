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
        window.smsViewModel = new SmsViewModel();
        window.pollViewModel = new PollViewModel();
        var poll_questionnaire_model = window.pollViewModel;
        poll_questionnaire_model.show_sms("poll_via_sms");
        poll_questionnaire_model.create_poll();

        expect(smsViewModel.smsOptionList()[0]['label']).toBe('Select Recipients');
        expect(smsViewModel.smsOptionList()[1]['label']).toBe('Group');
        expect(smsViewModel.smsOptionList()[2]['label']).toBe('Contacts linked to a Questionnaire');

    });

    it('should_validate_add_number_of_days', function(){
        window.pollViewModel = new PollViewModel();
        var pollViewModel = window.pollViewModel;
        var current_date = new Date();

        pollViewModel.number_of_days(5);
        pollViewModel.from_date_poll(current_date);
        pollViewModel.days_active();
        var expected_date = new Date();
        expected_date.setDate(current_date.getDate() + 5);
        var calculateDays = new CalculateDays(current_date.getDate() + 5, current_date);
        expect(pollViewModel.to_date_poll()).toBe(expected_date.getDate()+" "+ calculateDays.month_name_map[expected_date.getMonth()]+" "+  expected_date.getFullYear())

    });


});