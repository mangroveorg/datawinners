$(document).ready(function() {
    $('.credit_card').append(gettext("Call us directly and we can securely process your credit card payment over the phone"));
    $('.pay_via_ach').append(gettext("Securely transfer funds between your US-based bank account and ours (normally free of charge)."));

    $("#user_should_agree_terms_block").dialog({
        autoOpen: false,
        modal: true,
        title: gettext("DataWinners Terms & Conditions"),
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

    $("#cancel-agree-terms").bind("click", function(){
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

    $("[name=account_type],[name=invoice_period]").bind("click", function(){
        update_price();
    });

    function update_price(){
        var account_type = $("[name=account_type]:checked").val();
        var pricing = new Array();
        pricing['Pro SMS'] = new Array();
        pricing['Pro SMS']['pay_monthly_per_month'] = 399;
        pricing['Pro SMS']['pay_half_yearly_per_month'] = 359;
        pricing['Pro SMS']['pay_yearly_per_month'] = 299;
        pricing['Pro SMS']['pay_monthly'] = 399;
        pricing['Pro SMS']['half_yearly'] = 2154;
        pricing['Pro SMS']['yearly'] = 3588;

        pricing['Pro'] = new Array();
        pricing['Pro']['pay_monthly_per_month'] = 199;
        pricing['Pro']['pay_half_yearly_per_month'] = 149;
        pricing['Pro']['pay_yearly_per_month'] = 99;
        pricing['Pro']['pay_monthly'] = 199;
        pricing['Pro']['half_yearly'] = 894;
        pricing['Pro']['yearly'] = 1188;

        var invoice_period = $("input[name=invoice_period]:checked").val();

        $('#invoice_total_span').text(pricing[account_type][invoice_period]);

        for (dom_id in pricing[account_type]) {
            $("#" + dom_id).text(pricing[account_type][dom_id]);
        }
    }

    update_price();
});