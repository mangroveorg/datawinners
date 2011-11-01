$(document).ready(function() {



    $("#user_should_agree_terms_block").dialog({
        autoOpen: false,
        modal: true,
        title: gettext('Agree terms and conditions'),
        zIndex:200,
        width: 500,
        beforeClose: function() {
            $('#web_user_error').hide();
        }
    });

    $("#user_should_agree_terms_block .agree_link").bind("click", function() {
        $("#agree-terms").attr("checked", true);
        $("#user_should_agree_terms_block").dialog("close");
    });

    $('#submit_registration_form').bind("click", function() {
        if(!$("#agree-terms").attr("checked")){
            $("#user_should_agree_terms_block").dialog("open");
            return false;
        }

        $('#submit_registration_form').attr("disabled", true);
        $('#registration_form').submit();
    });
    
    $("#content_of_terms_and_conditions").load($("#link-terms-and-conditions").attr("href")+" #content-terms");

     $("#content_of_terms_and_conditions").dialog({
        autoOpen: false,
        modal: true,
        title: gettext('Terms And Conditions'),
        zIndex:200,
        width: 1000,
        beforeClose: function() {
            $('#web_user_error').hide();
        }
    });

    $("#link-terms-and-conditions").bind("click", function(){
        $("#content_of_terms_and_conditions").dialog("open");
        return false;
    });






});