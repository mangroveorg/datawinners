$(document).ready(function() {

        $('#on_behalf_of').on("click", function() {
            if ($(this).is(':checked')) {
                $('#choice_ds').removeClass("none");
            }
            else {
                $('#choice_ds').addClass("none");
                $('#on_behalf_of_error').parent().parent().addClass("none");
            }
            DW.trackEvent('web-submission','change-datasender');
        });

    var change_ds_dropdown = $("#id_dsid");
    if ($('ul.errorlist li span#on_behalf_of_error ').length || change_ds_dropdown.val()) {
            $('#choice_ds').removeClass("none");
            $('#on_behalf_of').attr("checked", "checked") ;
    }

    change_ds_dropdown.on('change', function(){
       DW.trackEvent('web-submission', 'choose-datasender-from-list');
    });

});
