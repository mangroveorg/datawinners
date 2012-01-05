$(document).ready(function() {
    $('.pay_monthly').append(gettext("Renews automatically each month. Cancel at any time without penalty."));
    $('.pay_half_yearly').append(gettext("Save 10% by paying 6 months in advance"));
    $('.credit_card').append(gettext("Call us directly and we can securely process your credit card payment over the phone"));
    $('.pay_via_ach').append(gettext("Securely transfer funds between your US-based bank account and ours (normally free of charge)."));

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
    
    //$("#content_of_terms_and_conditions").load($("#link-terms-and-conditions").attr("href")+" #content-terms");

    $("#content_of_terms_and_conditions").load($("#link-terms-and-conditions").attr("href")+" #container_main_content");

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

    $("#id_organization_country").autocomplete({
        source: function(req, response) {
	        var re = $.ui.autocomplete.escapeRegex(req.term);
	        var matcher = new RegExp( "^" + re, "i" );
	        response($.grep(countryList, function(item){return matcher.test(item); }) );
        }
    });

});