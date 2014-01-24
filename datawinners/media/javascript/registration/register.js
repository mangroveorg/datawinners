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
        if ($("[name=account_type]:checked").length == 0)
            return;
        
        var account_type = $("[name=account_type]:checked").val();
        var pricing = {
            'Pro SMS':{
                'invoice_period':{
                    'pay_monthly_per_month':399,
                    'pay_half_yearly_per_month':359,
                    'pay_yearly_per_month': 299,
                    'half_yearly_percentage': 10,
                    'yearly_percentage': 25
                },
                'totals':{
                    'pay_monthly':399,
                    'half_yearly':2154,
                    'yearly':3588
                }
            },
            'Pro':{
                'invoice_period':{
                    'pay_monthly_per_month':199,
                    'pay_half_yearly_per_month':149,
                    'pay_yearly_per_month': 99,
                    'half_yearly_percentage': 25,
                    'yearly_percentage': 50
                },
                'totals':{
                    'pay_monthly':199,
                    'half_yearly':894,
                    'yearly':1188
                }
            }
        }
        
        if  ($("input[name=invoice_period]:checked").length != 0) {
            var invoice_period = $("input[name=invoice_period]:checked").val();
            $('#invoice_total_span').text(pricing[account_type]['totals'][invoice_period]);
        }

        for (dom_id in pricing[account_type]['invoice_period']) {
            $("#" + dom_id).text(pricing[account_type]['invoice_period'][dom_id]);
        }
    }

    update_price();
});