DW.viewModel = {};

$(document).ready(function(){
    var validator = $('#question_form').validate();

    $('#autogen').unbind('change').change(function(event){

        if($('#autogen').attr('checked') != true){
            $('#short_name').addClass('required');
            $('#short_name').attr('disabled', '');

        }
        else{
            $('#short_name').removeClass('error');
            $('#short_name').removeClass('required');
            $('#short_name').val("");
            $('#short_name').attr('disabled', 'disabled');
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

