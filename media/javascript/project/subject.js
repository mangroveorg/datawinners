$(document).ready(function(){

    $('#autogen').unbind('change').change(function(event) {
           if ($('#autogen').attr('checked') != true) {
               $('#short_name').attr('disabled', '');

           }
           else {
               $('#short_name').removeClass('error');
               $("#short_name").parent().find('label.error').hide();
               $('#short_name').val("");
               $('#short_name').attr('disabled', 'disabled');
           }
       });

    $(".add_subject_form").dialog({
        autoOpen: false,
        width: 575,
        modal: true,
        title: 'Add A Subject',
        close: function() {
            $('#message').remove();
            $('#question_form').each (function(){
              this.reset();
            });
            DW.validator.resetForm();
        }
    });

     $("#add_subject").unbind('click').click(function() {
        $(".add_subject_form").dialog("open");
    });



    $('#register_entity').unbind('click').click(function() {
        if ($('#question_form').valid()) {
            var message = {'form_code':'reg',
                't':$('#id_entity_type').val(),
                's':$('#short_name').val(),
                'l':$('#location').val(),
                'd':$('#description').val(),
                'm':$('#mobile_number').val(),
                'n':$('#entity_name').val(),
                'g':$('#geo_code').val()
            };
            var data = {'message':message,'transport': 'web','source': 'web','destination': 'mangrove'};
            $.post('/submit', {'format': 'json', 'data': JSON.stringify(data, null, 1)},
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
});