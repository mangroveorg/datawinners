DW.viewModel = {};

$(document).ready(function() {

    $('#register_entity').unbind('click').click(function() {
        if ($('#question_form').valid()) {
            if (DW.viewModel.message.s())
                DW.viewModel.message.s(DW.viewModel.message.s().toLowerCase());
            $.post($('#post_url').val(), {'format': 'json', 'data': JSON.stringify(ko.toJS(DW.viewModel), null, 1)},
                    function(response) {
                        var d = JSON.parse(response);
                        $('#message').remove();
                        if (d.success) {
                            $('<span id="message" class="success_message">' + d.message + '</span>').insertBefore($('#question_form'));
                            $('#message').delay(10000).fadeOut();
                        }
                        else {
                            $('<span id="message" class="error_message">' + d.message + '</span>').insertBefore($('#question_form'));
                        }
                    }
            );
        }
    }
    );

    DW.viewModel = {
        'message': {
            'n': ko.observable(),
            's': ko.observable(),
            't': ko.observable(),
            'l': ko.observable(),
            'd': ko.observable(),
            'm': ko.observable(),
            'g': ko.observable(),
            'form_code': 'reg'
        },
        'transport': 'web',
        'source': 'web',
        'destination': 'mangrove'
    };
    ko.applyBindings(DW.viewModel);

});

