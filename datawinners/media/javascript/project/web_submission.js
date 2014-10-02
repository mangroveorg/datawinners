$(document).ready(function() {
        reporter_id = DW.reporter_id;
        is_linked = DW.is_linked;
        if (!is_linked){
            $('select#id_dsid option[value='+ reporter_id +']').addClass("display_none");
        }

        if (!($('#on_behal_of').is(':checked'))){
           $('select#id_dsid option[value='+ reporter_id +']').attr("selected", "selected");
        }
        else{
              $('select#id_dsid option:eq(0)').attr("selected", "selected");
        }
        $('#on_behalf_of').live("click", function() {
            if ($(this).is(':checked')) {
                $('#choice_ds').removeClass("display_none");
                $('select#id_dsid option:eq(0)').attr("selected", "selected");
            }
            else {
                $('#choice_ds').addClass("display_none");
            }
        });

        if ($('ul.errorlist li span#on_behalf_of_error ').length){
            $('#choice_ds').removeClass("display_none");
            $('#on_behalf_of').attr("checked", "checked") ;
            $('select#id_dsid option:eq(0)').attr("selected", "selected");
        }
    });
