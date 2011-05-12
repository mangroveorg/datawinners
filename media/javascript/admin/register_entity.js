DW.viewModel = {};

$(document).ready(function(){
    var validator = $('#question_form').validate();

    $('#register_entity').unbind('click').click(function() {
        if($('#question_form').valid())
        {
            $.post($('#post_url').val(), {'format': 'json', 'data': JSON.stringify(ko.toJS(DW.viewModel), null, 1)},
               function(response){
                    var d = JSON.parse(response);
                    $('#message').remove();
                    if(d.success)
                    {
                        $('<span id="message" class="success_message">' + d.message + '</span>').insertBefore($('#question_form'));
                        $('#message').delay(10000).fadeOut();
                    }
                    else
                    {
                        $('<span id="message" class="error_message">' + d.message + '</span>').insertBefore($('#question_form'));
                    }
               }
            );
        }
    });

    DW.viewModel = {
                    'message': {
                                'N': ko.observable(),
                                'S': ko.observable(),
                                'T': ko.observable(),
                                'L': ko.observable(),
                                'D': ko.observable(),
                                'M': ko.observable(),
                                'form_code': 'REG'
                                },
                    'transport': 'web',
                    'source': 'web',
                    'destination': 'mangrove'
                   };
    ko.applyBindings(DW.viewModel);

});

