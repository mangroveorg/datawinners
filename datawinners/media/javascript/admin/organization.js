(function($) {
    $(document).ready(function($) {
        django.jQuery("tr input.action-select").actions();

        var submit_button = $("#changelist-form button[type=submit]");

        $("select[name=action]").attr('disabled', 'disabled');

        var action = '';

        var warning_messages_by_actions = {"activate_organizations":gettext("Do you want to activate the account(s)?"),
                                           "deactivate_organizations":gettext("Do you want to deactivate the account(s)?"),
                                           "delete_organizations":gettext("Deleting accounts cannot be undone" +
                                                   "<br/>Are you sure you want to delete?"),
                                           "delete_active_accounts":gettext("You are trying to delete 1 or more active accounts."+
                                                   "<br/>Only deactivated accounts can be deleted.<br/><br/>Deactivate all account(s) first.")};

        var popup_titles = {"activate_organizations":gettext("Activate Account(s)"),
            "deactivate_organizations":gettext("Deactivate Account(s)"),
            "delete_organizations":gettext("The Accounts(s) will be Deleted"),
            "delete_active_accounts":gettext("Active Accounts(s) cannot be Deleted")}

        var confirm_caption = {"activate_organizations":gettext("Activate"),
            "deactivate_organizations":gettext("Deactivate"),
            "delete_organizations":gettext("Delete"),
            "delete_active_accounts":gettext("Ok")}

        $("button.button").css('display', 'none');

        $("#warning_popup").dialog({autoOpen:false, width:'auto', close:close_dialog, modal:true});


        $("tr input.action-select,input#action-toggle").click(function(){
            if ($("tr input.action-select:checked,input#action-toggle:checked").length) {
                $("select[name=action]").removeAttr('disabled');
            } else {
                $("select[name=action]").attr('disabled','disabled');
            }
        });

        $("select[name=action]").change(function(){

            var action_selected = $(this).attr("value");
            $("#warning_popup").dialog("option", "title", "");
            $("#perform_action").css("display","inline");
            $("#cancel_action").val(gettext("Cancel"));

            if (action_selected){
                submit_button.attr("disabled","disabled");
                $("#warning_message").html(warning_messages_by_actions[action_selected]);
                $("#warning_popup").dialog("option", "title", popup_titles[action_selected]);
                $("#perform_action").val(confirm_caption[action_selected]);

                if (action_selected == "delete_organizations") {
                    var index_of_status = $("#result_list thead th").index($("#result_list thead th:contains('Status')")) +1;
                    var selected_contains_active = false;

                    $("#result_list tbody tr.selected").each(function(index, element){
                        if ($(this).find("td:nth-child("+index_of_status+")").html() == gettext("Activated")) {
                            selected_contains_active = true;
                        }
                    });

                    if (selected_contains_active) {
                        $("#warning_message").html(warning_messages_by_actions['delete_active_accounts']);
                        $("#cancel_action").val(confirm_caption['delete_active_accounts']);
                        $("#perform_action").css("display","none");
                        $("#warning_popup").dialog("option", "title", popup_titles['delete_active_accounts']);
                    }
                }

                $("#warning_popup").dialog("open");
            }
        });

        $("#perform_action").bind("click", function(){
            action = $("select[name=action]").val();
            $("#warning_popup").dialog("close");
        });

        $("#cancel_action").bind("click", function(){
            action = '';
            $("#warning_popup").dialog("close");
        });

        function close_dialog(){
            submit_button.removeAttr("disabled");
            if (action) {
                submit_button.trigger("click");
            }
            $("select[name=action]").val("");
        }
    });
})(jQuery);