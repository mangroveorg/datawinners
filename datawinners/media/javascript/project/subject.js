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
        width: 600,
        modal: true,
        title: gettext('Add A Subject'),
        open:function(){
            $("#add_subject_type_content").addClass("none");
        },
        close: function() {
            $('#message').remove();
            $("#add_subject_type").accordion({collapsible: true,autoHeight:false, active:false});
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
        $("#add_subject_type").accordion({active:false});
        $(".add_subject_form").dialog("close");
    });
});
