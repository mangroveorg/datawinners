$(document).ready(function () {
    var allIds = [];

    function updateIds() {
        allIds = [];
        $('#tbody :checked').each(function () {
            allIds.push($(this).val());
        });
    }

    $("input[type='checkbox']").each(function () {
        $(this).change(function () {
            var selected_count = $('#tbody :checked').length;
            if (selected_count > 1) {
                $("select option[value='edit']").attr('disabled', 'disabled')
            } else {
                $("select option[value='edit']").removeAttr('disabled');
            }
        })
    });

    $('#action li a').click(function (e) {
        updateIds();
        $('#error').remove();
        var action = this.className;
        if (action == 'disassociate') {
            DW.loading();
            $.post('/project/disassociate/',
                {'ids':allIds.join(';'), 'project_id':$("#project_id").val()}
            ).success(function (data) {
                    $("button.action").dropdown("detach");
                    $('<div class="success-message-box clear-left" id="success_message">' + gettext("Data Senders dissociated Successfully") + '. ' + gettext("Please Wait") + '....</div>').insertAfter($('#action_dropdown'));
                    $('#success_message').delay(4000).fadeOut(1000, function () {
                        $('#success_message').remove();
                    });
                    setTimeout(function () {
                        window.location.reload(true);
                    }, 5000);
                }
            );
        } else if (action == 'delete') {
            $(this).val('');
            $("#note_for_delete_users").hide();
            var users = DW.get_is_user();
            if (users["names"].length) {
                var users_list_for_html = "<li>" + users["names"].join("</li><li>") + "</li>";

                if (users["names"].length == allIds.length) { //Each DS selected is also User

                    $(delete_all_ds_are_users.container + " .users_list").html(users_list_for_html);
                    delete_all_ds_are_users.show_warning();

                } else {                                      // A mix of Simple DS and DS having user credentials

                    $("#note_for_delete_users .users_list").html(users_list_for_html);
                    $("#note_for_delete_users").show();
                    DW.uncheck_all_users();
                    updateIds();
                    warnThenDeleteDialogBox(allIds, "reporter", this);

                }
            } else {
                warnThenDeleteDialogBox(allIds, "reporter", this);
            }
        } else if (action == 'edit') {
            if (allIds.length > 1 || $(this).parent().hasClass("disabled")) {
                e.preventDefault();
                return false;
            } else {
                location.href = '/project/datasender/edit/' + $("#project_id").val() + '/' + allIds[0] + '/';
            }
        }
    });

    var kwargs = {
        checkbox_locator:"#associated_data_senders input:checkbox",
        many_selected_msg: gettext("Please select only 1 Data Sender"),
        check_single_checked_locator: "#associated_data_senders tbody input:checkbox[checked=checked]",
        no_cb_checked_locator: "#associated_data_senders input:checkbox[checked=checked]",
        edit_link_locator: "#edit",
        container: document
    }
    DW.registered_ds_action_dropdown = new DW.action_dropdown(kwargs);

    $("#checkall-datasenders").bind("click", function(){
        var checked = $(this).attr("checked") == "checked";
        $("#associated_data_senders tbody input").attr("checked", checked);

        if (!checked) {
            DW.registered_ds_action_dropdown.deactivate_action();
        } else {
            DW.registered_ds_action_dropdown.update_edit_action();
        }

    });

    $("#associated_data_senders tbody input").bind("click", function(){
        var checked = $("#associated_data_senders tbody input:checkbox").length == $("#associated_data_senders tbody input:checkbox[checked]").length;
        $("#checkall-datasenders").attr("checked", checked);
    });

    if ($("#associated_data_senders tbody input:checkbox").length == 0) {
        $("#checkall-datasenders").attr("disabled", "disabled");
    }
});



