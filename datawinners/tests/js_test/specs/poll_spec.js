/**
 * Created by vikas on 6/10/15.
 */

describe("Deactivate Poll", function() {

    it('should_deactivate_poll', function () {
        window.smsViewModel = new SmsViewModel();
        window.pollOptions = new PollOptionsViewModel()
        var sms_view_model = window.smsViewModel
        var poll_options = window.pollOptions

        poll_options.deactivate();
        poll_options.deactivate_poll();

//        expect(questionnaire_view_model.projectName.error()).toBe('This field is required');

    });

});