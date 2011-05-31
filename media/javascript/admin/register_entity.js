DW.viewModel = {};

$(document).ready(function(){
    var validator = $('#question_form').validate();

    $('#autogen').unbind('change').change(function(){
        if($('#autogen').attr('checked') != true){
            $('#short_name').attr('disabled', '');
            $('#short_name').addClass('required');
        }
        else{
            $('#short_name').attr('disabled', 'disabled');
            $('#short_name').val("");
            $('#short_name').removeClass('required');
            DW.viewModel.message.s=ko.observable("")
        }
    })

    $('#register_entity').unbind('click').click(function() {
        if($('#question_form').valid())
        {
            $.post($('#post_url').val(), {'format': 'json', 'data': JSON.stringify(ko.toJS(DW.viewModel), null, 1)},
               function(response){
                    var d = JSON.parse(response);
                    $('#message').remove();
                    if(d.success)
                    {
                        $('<span id="message" class="success_message">' + d.message  + '</span>').insertBefore($('#question_form'));
                        $('#message').delay(10000).fadeOut();
                    }
                    else
                    {
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
                                'form_code': 'REG'
                                },
                    'transport': 'web',
                    'source': 'web',
                    'destination': 'mangrove'
                   };
    ko.applyBindings(DW.viewModel);

});

