/**
 * Created by vikas on 6/10/15.
 */

describe("Deactivate Poll", function() {

    it('should_deactivate_poll', function () {
        window.smsViewModel = new SmsViewModel();
        window.pollOptions = new PollOptionsViewModel();
        var poll_options = window.pollOptions;
        poll_options.deactivationDialogVisible(true);
//        poll_options.deactivate_poll();

        spyOn(jQuery, "ajax").andCallFake(function(params) {
            var d = $.Deferred();
            d.resolve([{"success":true}]);
            params.success(true)
            return d.promise();
        });

        expect($.ajax.mostRecentCall.args[0]).toEqual(deactivate_poll_url);
        expect(poll_options.status()).toBe('Deactivated')

    });

});