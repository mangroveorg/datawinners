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
        title: gettext('Add A Subject'),
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

    $(".cancel_link").unbind('click').click(function(event) {
        event.preventDefault();
        $(".add_subject_form").dialog("close");
    });

});
