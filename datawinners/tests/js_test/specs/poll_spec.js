/**
 * Created by vikas on 6/10/15.
 */

describe("Deactivate Poll", function() {

    xit('should_deactivate_poll', function () {
        window.smsViewModel = new SmsViewModel();
        window.pollOptions = new PollOptionsViewModel();
        var poll_options = window.pollOptions;
//        poll_options.deactivationDialogVisible(true);
        var responseJSON ='{"success":true}';

        spyOn(jQuery, "ajax").andCallFake(function() {
            var d = $.Deferred();
            d.resolve(responseJSON);
            return d.promise();
        });
        poll_options.deactivate_poll();
//        expect($.ajax.mostRecentCall.args[0]['url']).toEqual(deactivate_poll_url);
//        expect(poll_options.status()).toBe('Deactivated')

    });

});