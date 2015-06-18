/**
 * Created by vikas on 6/10/15.
 */

describe("Deactivate Poll", function() {

    it('should_deactivate_poll', function () {
        window.pollOptions = new PollOptionsViewModel();
        var poll_options = window.pollOptions;
        poll_options.number_of_days(4);

        spyOn(jQuery, "ajax").andCallFake(function() {
            var d = $.Deferred();
            d.resolve('{"success":true}');
            return d.promise();
        });

        poll_options.deactivate_poll();
        expect($.ajax.mostRecentCall.args[0]['url']).toEqual("http://deactivate_poll_url.com");
        expect($.ajax.mostRecentCall.args[0]["type"]).toEqual("post");
        expect($.ajax.mostRecentCall.args[0]["data"]).toEqual({});

        expect(poll_options.status()).toBe('Deactivated');
        expect(poll_options.duration()).toBe('is inactive');
        expect(poll_options.activation()).toBe('Activate');
        expect(poll_options.deactivation()).toBe('');
        expect(poll_options.number_of_days()).toBe(1);

    });

});

describe("Activate Poll", function() {

    it('should activate poll', function () {
        window.pollOptions = new PollOptionsViewModel();
        var poll_options = window.pollOptions;
        poll_options.number_of_days(2);
        var current_date = new Date();
        poll_options.from_date_poll(current_date);

        spyOn(jQuery, "ajax").andCallFake(function() {
            var d = $.Deferred();
            d.resolve('{"success":true}');
            return d.promise();
        });

        var expected_date = new Date();
        expected_date.setDate(current_date.getDate()+2);
        var expected_end_date = expected_date.getFullYear() + "-" + (expected_date.getMonth() + 1) + "-" + expected_date.getDate();
        poll_options.activate_poll();

        expect($.ajax.mostRecentCall.args[0]['url']).toEqual("http://activate_poll_url.com");
        expect($.ajax.mostRecentCall.args[0]["type"]).toEqual("post");
        expect($.ajax.mostRecentCall.args[0]["data"]).toEqual({"end_date": expected_end_date + "T23:59:00"});

        expect(poll_options.status()).toBe('Active');
        expect(poll_options.from_date_poll()).toBe(current_date);
        expect(poll_options.to_date_poll()).toBe(poll_options.get_formatted_date(expected_date));
        expect(poll_options.duration()).toBe('is active From '+current_date +' To '+poll_options.get_formatted_date(expected_date));
        expect(poll_options.activation()).toBe('');
        expect(poll_options.deactivation()).toBe('Deactivate');
        expect(poll_options.number_of_days()).toBe(2);
    });

});