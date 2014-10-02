$(document).ready(function() {

        $('#on_behalf_of').live("click", function() {
            if ($(this).is(':checked')) {
                $('#choice_ds').removeClass("none");
            }
            else {
                $('#choice_ds').addClass("none");
                $('ul.errorlist li span#on_behalf_of_error').parent().parent().addClass("none");
            }
        });

        if ($('ul.errorlist li span#on_behalf_of_error ').length || $("#id_dsid").val()) {
            $('#choice_ds').removeClass("none");
            $('#on_behalf_of').attr("checked", "checked") ;
        }
    });
