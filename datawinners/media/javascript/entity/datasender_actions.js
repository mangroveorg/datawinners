
function warnThenDeleteDialogBox(allIds, all_selected, entity_type, action_element) {
   //$("#delete_ds_block").dialog();
    var delete_dialog = $("#delete_ds_block").dialog({
            title: gettext("Warning !!"),
            modal: true,
            autoOpen: true,
            width: 500,
            closeText: 'hide'
        }
    );

    delete_dialog.data("allIds", allIds);
    delete_dialog.data("all_selected", all_selected);
    delete_dialog.data("entity_type", entity_type);
    delete_dialog.data("action_element", action_element);

     $("#delete_ds_block .cancel_link").click(function() {
         delete_dialog.dialog("close");
        $('#delete_ds_block').data("action_element").value = "";
        return false;
    });


    $("#delete_ds_block #ok_button").click(function() {
        delete_dialog.dialog("close");
        var allIds = delete_dialog.data("allIds");
        var all_selected = delete_dialog.data("all_selected");
        var entity_type = delete_dialog.data("entity_type");
        post_data = {'ids':allIds.join(';'), 'entity_type':entity_type, 'all_selected':all_selected, 'search_query':$(".datasender_table_filter input").val()}
        if ($("#project_name").length)
            post_data.project = $("#project_name").val();
        if(all_selected)
            post_data.all_selected = true;
        DW.loading();
        $.post("/entity/delete/", post_data,
            function (json_response) {
                var response = $.parseJSON(json_response);
                flash_message(response.message, response.success);
                if (response.success) {
                    $("#datasender_table").dataTable().fnReloadAjax();
                }
            }
        );
        return false;
    });


    delete_dialog.dialog("open");
}


DW.DataSenderActionHandler = function(){
  this["delete"] = function(table, selected_ids, all_selected){
        handle_datasender_delete(table, selected_ids, all_selected);
  };
  this["edit"] = function(table, selected_ids){
    location.href = '/entity/datasender/edit' + '/' + selected_ids[0] + '/';
  };
  this["makewebuser"] = function(table, selected_ids, all_selected){
    populate_dialog_box_for_web_users(table, all_selected);
  };
  this["associate"] = function(table, selected_ids, all_selected){
    add_remove_from_project('associate', table, selected_ids, all_selected);
  };
  this["disassociate"] = function(table, selected_ids, all_selected){
    add_remove_from_project('disassociate', table, selected_ids, all_selected);
  };
  this["mydsedit"] = function(table, selected_ids){
    location.href = '/project/datasender/edit/' + $("#project_id").val() + '/' + selected_ids[0] + '/';
  };
  this["remove_from_project"] = function(table, selectedIds, all_selected) {
            DW.loading();
            $.ajax({'url':'/project/disassociate/', 'type':'POST', headers: { "X-CSRFToken": $.cookie('csrftoken') },
                data: {'ids':selectedIds.join(';'), 'project_id':$("#project_id").val()}
            }).done(function (data) {
                    table.fnReloadAjax();
                    flash_message("Data Senders dissociated Successfully");
                }
            );
        };

};

function flash_message(msg, status){
    $('.flash-message').remove();

    $(".dataTables_wrapper").prepend('<div class="clear-left flash-message">' + gettext(msg) + (msg.match("[.]$")?'':'.') + '</div>')
    $('.flash-message').addClass((status === false)?"message-box":"success-message-box");

    $('#success_message').delay(4000).fadeOut(1000, function () {
        alert('timeout');
        $('.flash-message').remove();
    });
}

function add_remove_from_project(action,  table, selected_ids, all_selected) {
    $("#all_project_block").dialog({
        autoOpen: false,
        modal: true,
        title: gettext('Select Projects'),
        zIndex: 1100,
        beforeClose: function () {
            $('#action').at;
        }
    });
    $("#all_project_block").find('#error').remove();
    $('#all_project_block :checked').attr("checked",false);

    $("#all_project_block .cancel_link").bind("click", function () {
        $("#all_project_block").dialog("close");
    });

    $("#all_project_block .button").bind("click", function () {

        var projects = [];
        $('#all_project_block :checked').each(function () {
            projects.push($(this).val());
        });
        if (projects.length == 0) {
            $('<div class="message-box" id="error">' + gettext("Please select atleast 1 Project")
                + '</div>').insertBefore($("#all_projects"));
        } else {
            var url = '/entity/' + action + '/';
            $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">'
                + gettext("Just a moment") + '...</span></h1>', css: { width: '275px', zIndex: 1000000}});
            $.ajax({
                        url: url,
                        type: "POST",
                        headers: { "X-CSRFToken": $.cookie('csrftoken') },
                    data: {
                            'ids': selected_ids.join(';'),
                            'project_id': projects.join(';'),
                            'all_selected': all_selected,
                            'search_query':$(".dataTables_filter input").val()
                        }

            }).done(function (data) {
                    $("#all_project_block").dialog('close');
                    $("#datasender_table").dataTable().fnReloadAjax();
                });
        }
    });

    $("#all_project_block").dialog("open");
}

get_users_from_selected_datasenders = function (table, selected_ids) {
    var users = {};
    users["ids"] = [];
    users["names"] = [];
    $(table).find('input.row_checkbox:checked').each(function () {
        var datasender_id = $(this).val();
        if ($.inArray(datasender_id ,users_list) >= 0) {
            users["ids"].push(datasender_id);
            users["names"].push($(this).parent().next().html());
        }
    });

    return users;
}

function delete_all_ds_are_users_show_warning(users) {


    var kwargs = {container: "#delete_all_ds_are_users_warning_dialog",
        autoOpen: false,
        cancel_handler: function () {
            $('#action').removeAttr("data-selected-action");
            $("input.is_user").attr("checked", false);
        },
        height: 180,
        width: 550
    }

    $(kwargs.container + " .users_list").html(users);
    var delete_all_ds_are_users = new DW.warning_dialog(kwargs);
    delete_all_ds_are_users.show_warning();
}

function uncheck_users(table, user_ids){
    $.each(user_ids, function(id){
        $(table).find(":checked").filter("[value=" + id + "]").attr('checked',false);
    });
    return $.map($(table).find("input.row_checkbox:checked"), function(e){return $(e).val();});
}

function handle_datasender_delete(table, allIds, all_selected){
    $("#note_for_delete_users").hide();
    var settings = table.fnSettings();
    if (settings.fnDisplayEnd() == settings.fnRecordsDisplay()){
        if ($(table).find("input.row_checkbox").length == allIds.length){
           settings._iDisplayStart = 0;
        }
    }

    var users = get_users_from_selected_datasenders(table, allIds);

    if (users["names"].length) {
        var users_list_for_html = "<li>" + users["names"].join("</li><li>") + "</li>";
        if (users["names"].length == allIds.length) { //Each DS selected is also User

            delete_all_ds_are_users_show_warning(users_list_for_html);
        } else { // A mix of Simple DS and DS having user credentials
            $("#note_for_delete_users .users_list").html(users_list_for_html);
            $("#note_for_delete_users").show();
            allIds = uncheck_users(table, users["ids"]);
            warnThenDeleteDialogBox(allIds, all_selected, "reporter", this);
        }
    } else {
        warnThenDeleteDialogBox(allIds, all_selected, "reporter", this);
    }
}


function populate_dialog_box_for_web_users(table, all_selected) {
    if (all_selected) {
        var total_records = table.fnSettings().fnRecordsDisplay();
        var current_page_size = table.fnSettings()._iDisplayLength;
        $("#all_selected_message").show();
        $("#all_selected_message").text(
            interpolate(gettext('all_selected_message %(total_records)s %(current_page_size)s'),
                {total_records: total_records, current_page_size: current_page_size}, true));
    } else {
        $("#all_selected_message").hide();
    }

    var data_sender_details = [];
    $(table).find("input.row_checkbox:checked").each(function () {
        var row = $(this).parent().parent();
        var data_sender = {};
        data_sender.short_name = $($(row).children()[2]).html();
        data_sender.name = $($(row).children()[1]).html();
        data_sender.location = $($(row).children()[4]).html();
        data_sender.contactInformation = $($(row).children()[8]).html();
        data_sender.email = $($(row).children()[6]).html();
        data_sender.input_field_disabled = "disabled";
        if (!$.trim(data_sender.email)) {
            data_sender.input_field_disabled = "";
            data_sender.email = "";
        } else {
            data_sender.hideInput = "none";
        }

        data_sender_details.push(data_sender);
    });
     var markup = "<tr><td>${short_name}</td><td>${name}</td><td style='width:150px;'>" +
        "${location}</td><td>${contactInformation}</td><td>" +
        "<input type='text' style='width:150px' class='ds-email ${hideInput}' ${input_field_disabled}/>" +
        "<label style='font-weight:inherit'>${email}</label>" +
         "</td></tr>";
    $.template("webUserTemplate", markup);
    $('#web_user_table_body').html($.tmpl('webUserTemplate', data_sender_details));
    $("#web_user_block").dialog({
        autoOpen: false,
        modal: true,
        title: gettext('Give Web Submission Access'),
        zIndex: 1100,
        width: 900,
        beforeClose: function () {
            $('#action').removeAttr("data-selected-action");
            $('#web_user_error').hide();
        }
    });
    $("#web_user_block .cancel_link").bind("click", function () {
        $("#web_user_block").dialog("close");
    });

    $('#web_user_button').click(function () {
        $('#web_user_error').hide();
        var post_data = [];
        var should_post = true;
        $('input:enabled.ds-email').each(function () {
            var email = $.trim($(this).val());
            var emailRegEx = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i;
            if (email == "") {
                $('#web_user_error').html(gettext('Emails are mandatory'));
                $('#web_user_error').removeClass('none');
                $('#web_user_error').show();
                should_post = false;
                return false;
            }
            if ($.trim(email).search(emailRegEx) == -1) {
                $('#web_user_error').removeClass('none');
                $('#web_user_error').html(email + gettext(": is not a valid email"));
                $('#web_user_error').show();
                should_post = false;
                return false;
            }
            var reporter_id = $($(this).parent().parent().children()[0]).html();
            post_data.push({email: email, reporter_id: reporter_id});
        });
        if (!should_post || post_data.length == 0) {
            return;
        }
        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">'
            + gettext("Just a moment") + '...</span></h1>', css: { width: '275px', zIndex: 1000000}});
        $.post('/entity/webuser/create', {post_data: JSON.stringify(post_data)},
            function (response) {
                $.unblockUI();
                var json_data = JSON.parse(response);
                if (json_data.success) {
                    $("#web_user_block").dialog("close");
                    table.fnReloadAjax();
                    flash_message("Access to Web Submission has been given to your DataSenders");
                } else {
                    var html = "";
                    var i = 0;
                    for (i; i < json_data.errors.length; i = i + 1) {
                        var email_in_error = json_data.errors[i].split(' ')[3];
                        var error_message = gettext('User with email ') + email_in_error + gettext(' already exists');
                        html += "<tr><td>" + error_message + "</td></tr>";
                    }
                    if (html != "") {
                        html = '<table cellpadding="0" cellspacing="0" border="0">' + html + '</table>';
                    }
                    $('#web_user_error').removeClass('none');
                    $('#web_user_error').html(html);
                    $('#web_user_error').show();
                }
            });
        return false;
    });


    $("#web_user_block").dialog("open")
}