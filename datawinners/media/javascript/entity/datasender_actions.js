function warnThenDeleteDialogBox(allIds, all_selected, entity_type, action_element) {
    var delete_dialog = $("#delete_ds_block");
    delete_dialog.data("allIds", allIds);
    delete_dialog.data("all_selected", all_selected);
    delete_dialog.data("entity_type", entity_type);
    delete_dialog.data("action_element", action_element);
    delete_dialog.data("pageToGo", get_updated_table_page_index($("#datasender_table").dataTable(), allIds, all_selected));
    delete_dialog.dialog("open");
}

function init_warnThenDeleteDialogBox() {
    var delete_dialog = $("#delete_ds_block").dialog({
            title: gettext("Warning!"),
            modal: true,
            autoOpen: false,
            width: 500,
            closeText: 'hide'
        }
    );

    $("#delete_ds_block .cancel_link").click(function () {
        delete_dialog.dialog("close");
        $('#delete_ds_block').data("action_element").value = "";
        return false;
    });


    $("#delete_ds_block #ok_button").click(function () {
        delete_dialog.dialog("close");
        var allIds = delete_dialog.data("allIds");
        var all_selected = delete_dialog.data("all_selected");
        var entity_type = delete_dialog.data("entity_type");
        post_data = {'ids': allIds.join(';'), 'entity_type': entity_type, 'all_selected': all_selected, 'search_query': $(".dataTables_filter input").val()}
        if ($("#project_name").length)
            post_data["project_name"] = $("#project_name").val().toLowerCase();
        if(all_selected)
            post_data["all_selected"] = true;
        DW.loading();
        $.post("/entity/delete/", post_data,
            function (json_response) {
                var response = $.parseJSON(json_response);
                DW.flashMessage(response.message, response.success);
                if (response.success) {
                    var table = $("#datasender_table").dataTable();
                    table.fnSettings()._iDisplayStart = delete_dialog.data("pageToGo");
                    table.fnReloadAjax();
                }
            }
        );
        return false;
    });
}

DW.DataSenderActionHandler = function () {

    init_dialog_box_for_web_users();
    init_warnThenDeleteDialogBox();
    init_add_remove_from_project();
    init_dialog_box_for_datasender();

    this["delete"] = function(table, selected_ids, all_selected){
        selected_ids= $.map(selected_ids, function(e){return e.toLowerCase();});
        handle_datasender_delete(table, selected_ids, all_selected);
    };
    this["edit"] = function (table, selected_ids) {
        handle_datasender_edit(table, selected_ids);
    };
    this["makewebuser"] = function (table, selected_ids, all_selected){
        populate_dialog_box_for_web_users(table, all_selected);
    };
    this["associate"] = function (table, selected_ids, all_selected){
       add_remove_from_project('associate', table, selected_ids, all_selected);
    };
    this["disassociate"] = function (table, selected_ids, all_selected) {
        add_remove_from_project('disassociate', table, selected_ids, all_selected);
    };
    this["sendAMessage"] = function (table, selected_ids, all_selected) {
        _populateAndShowSmsDialog(selected_ids, all_selected);

    };
    this["mydsedit"] = function (table, selected_ids) {
        handle_datasender_edit(table, selected_ids);
    };
    this["addtogroups"] = function(table, selected_ids, all_selected){
        _add_contact_to_group(selected_ids, all_selected);
    };

    this["removefromgroups"] = function(table, selected_ids, all_selected){
        _remove_from_group(selected_ids, all_selected);
    };

    this["remove_from_project"] = function(table, selectedIds, all_selected) {
        DW.loading();
        table.fnSettings()._iDisplayStart = get_updated_table_page_index(table, selectedIds, all_selected);
        $.ajax({'url':'/project/disassociate/', 'type':'POST', headers: { "X-CSRFToken": $.cookie('csrftoken') },
            data: { 'ids':selectedIds.join(';'),
                    'project_name':$("#project_name").val().toLowerCase(),
                    'project_id':$("#project_id").val(),
                    'all_selected':all_selected,
                    'search_query':$(".dataTables_filter input").val()
                  }
        }).done(function (json_response) {
                table.fnReloadAjax();
                var response = $.parseJSON(json_response);
                DW.flashMessage(response.message, response.success);
            }
        );
    };
};

function _add_contact_to_group(selected_ids, all_selected) {
    DW.loading();
    $.get(all_groups_url).done(function (response) {
            var allGroupsSection = $("#all_groups");
            allGroupsSection.html("");
            var groupNames = _.map(response.group_details, function(groupItem){ return groupItem.name;});
            _populate_group_dialog(groupNames);
            allGroupsSection.data("selected_ids", selected_ids);
            allGroupsSection.data("all_selected", all_selected);
            allGroupsSection.data("action", "add");
            allGroupsSection.data("current_group_name", selected_group);

            init_dialog_box_for_group();
            $('#no_group_selected_message').addClass('none');

            $('.add_or_remove').text(gettext("Add"));
            $('#all_groups_block').dialog("option", "title", gettext('Add to Groups'));
            $('#all_groups_block').dialog("open");
        }
    );
}

function _post_populating_of_remove_group_list(selected_ids, all_selected){
    var allGroupsSection = $("#all_groups");
    allGroupsSection.data("selected_ids", selected_ids);
    allGroupsSection.data("all_selected", all_selected);
    allGroupsSection.data("action", 'remove');
    allGroupsSection.data("current_group_name", selected_group);

    init_dialog_box_for_group();
    $('#no_group_selected_message').addClass('none');

    $('.add_or_remove').text(gettext("Remove"));
    $('#all_groups_block').dialog("option", "title", gettext('Remove from Groups'));
    $('#all_groups_block').dialog("open");
}

function _populate_group_dialog(groupNames){
    var allGroupsSection = $("#all_groups");
    $.each(groupNames, function (index, group_name) {
        allGroupsSection.append($("<li><label><input type='checkbox' value='" + group_name + "'>" + group_name + "</label></li>"));
    });
}

function _remove_from_group(selected_ids, all_selected) {
    if(all_selected){
            DW.loading();
            $.get(all_groups_url).done(function (response) {
                var allGroupsSection = $("#all_groups");
                allGroupsSection.html("");
                var groupNames = _.map(response.group_details, function(groupItem){ return groupItem.name;});
                _populate_group_dialog(groupNames);
                _post_populating_of_remove_group_list(selected_ids, all_selected);
            }
        );
    }
    else{
        var all_selected_groups = []
         $.each(selected_ids, function(index, rep_id){
            var children = $("input[value=" + rep_id + "]").closest("tr").children();
            var group_names = $(children[9]).text().split(", ");
             $.each(group_names, function(index, group_name){
                 if(group_name != ""){
                     all_selected_groups.push(group_name);
                 }
             });
         });
        var sorted_unique_group_names = _.sortBy(_.union(all_selected_groups), function(group_name){return group_name.toLowerCase(); });
        var allGroupsSection = $("#all_groups");
        allGroupsSection.html("");
        _populate_group_dialog(sorted_unique_group_names);
        _post_populating_of_remove_group_list(selected_ids, all_selected);
    }
}

function _populateAndShowSmsDialog(selected_ids, all_selected){
    if(all_selected){

        $.ajax({
            url: all_contacts_mobile_number_url,
            type: "POST",
            headers: { "X-CSRFToken": $.cookie('csrftoken') },
            data: {
                'group_name':selected_group,
                'search_query':$(".dataTables_filter input").val()
            }

        }).done(function (json_response) {
            var response =  $.parseJSON(json_response);
            _showSmsDialog(response['mobile_numbers'], response["contact_display_list"]);
        });

    }
    else{
        var contact_mobile_numbers = [];
        var contact_display_list = [];
        $.each(selected_ids, function(index, rep_id){
            var children = $("input[value=" + rep_id + "]").closest("tr").children();
            var mobile_number = $(children[2]).text();
            var contact_name = $(children[1]).text();
            var display_text = contact_name == "" ? mobile_number : contact_name
            contact_display_list.push(display_text + " ("+ rep_id +")");
            contact_mobile_numbers.push(mobile_number);
        });
        _showSmsDialog(contact_mobile_numbers.join(", "), contact_display_list.join(", "));
    }
}

function _showSmsDialog(contact_mobile_numbers, contact_display_list){
    var smsViewModel = ko.contextFor($("#send-sms-section")[0]).$root;
    smsViewModel.showToSection(false);
    smsViewModel.hideSpecifiedContacts(false);
    smsViewModel.selectedSmsOption("others");
    smsViewModel.othersList(contact_mobile_numbers);
    smsViewModel.specifiedList(contact_display_list);
    $("#send-sms-section").dialog('open');
}

function flash_message(msg, status) {
    DW.flashMessage(msg, status);
}

function init_add_remove_from_project() {
    var all_project_block = $("#all_project_block").dialog({
        autoOpen: false,
        modal: true,
        title: gettext('Add to Questionnaire'),
        zIndex: 1100,
        beforeClose: function () {
            $('#action').at;
        }
    });

    $("#all_project_block .cancel_link").bind("click", function () {
        all_project_block.dialog("close");
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
            var action = all_project_block.data("action");
            var url = '/entity/' + action + '/';
            $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">'
                + gettext("Just a moment") + '...</span></h1>', css: { width: '275px', zIndex: 1000000}});
            $.ajax({
                        url: url,
                        type: "POST",
                        headers: { "X-CSRFToken": $.cookie('csrftoken') },
                    data: {
                            'ids': $.map(all_project_block.data("selected_ids"), function(e){return e.toLowerCase();}).join(';'),
                            'project_id': projects.join(';'),
                            'all_selected': all_project_block.data("all_selected"),
                            'search_query':$(".dataTables_filter input").val()
                        }

            }).done(function (json_response) {
                    var table = $("#datasender_table").dataTable();
                    if (action == "disassociate") {
                        table.fnSettings()._iDisplayStart = all_project_block.data("pageToGo");
                    }
                    $("#all_project_block").dialog('close');
                    table.fnReloadAjax();
                    var response = $.parseJSON(json_response);
                    DW.flashMessage(response.message, response.success);
                });
        }
    });
}

function add_remove_from_project(action, table, selected_ids, all_selected) {
    var all_project_block = $("#all_project_block");
    all_project_block.find('#error').remove();
    $('#all_project_block :checked').attr("checked", false);
    all_project_block.data("selected_ids", selected_ids);
    all_project_block.data("all_selected", all_selected);
    all_project_block.data("action", action);
    all_project_block.data("pageToGo", get_updated_table_page_index(table, selected_ids, all_selected));
    if(action == 'associate') {
        $('#action_for_project').text(gettext("Add"));
        all_project_block.dialog('option', 'title', gettext('Add to Questionnaire'));
    }
    else {
        $('#action_for_project').text(gettext("Remove"));
        all_project_block.dialog('option', 'title', gettext('Remove from Questionnaire'));
    }
    all_project_block.dialog("open");
}
function get_user_names_from_selected_datasenders(table, selected_ids, all_selected) {
    var users =[];
    var user_rep_ids = [];
    var user_fullnames = [];
    $.each(user_dict, function(k,v) {
            user_rep_ids.push(k);
            user_fullnames.push(v)
        }
    );

    if (all_selected) {
        users = usersInSearchedDS();
    }else {
        $(table).find('input.row_checkbox:checked').each(function () {
            var datasender_id = $(this).val();
            if ($.inArray(datasender_id ,user_rep_ids) >= 0) {
                  users.push(user_dict[datasender_id])
            }
        });
    }
    return users;
}


function usersInSearchedDS() {
    var superusers;
    // synchronous
    $.ajax({
        async: false,
        url: superusersearch_ajax_url,
        type: "POST",
        headers: { "X-CSRFToken": $.cookie('csrftoken') },
        data: {
            'all_selected': true,
            'search_query':$(".dataTables_filter input").val(),
            'project_name':$("#project_name").val().toLowerCase()
        }

    }).done(function (json_response) {
            var response = $.parseJSON(json_response);
            superusers = response.superusers_selected;
    });

    return superusers;
}

function delete_all_ds_are_users_show_warning(users) {

    var kwargs = {container: "#delete_all_ds_are_users_warning_dialog",
        autoOpen: false,
        cancel_handler: function () {
            $('#action').removeAttr("data-selected-action");
            $("input.is_user").attr("checked", false);
        },
        width: 550,
        height: "auto"
    }

    $(kwargs.container + " .users_list").html(users);
    var delete_all_ds_are_users = new DW.warning_dialog(kwargs);
    delete_all_ds_are_users.show_warning();
}

function uncheck_users(table, user_ids) {
    $.each(user_ids, function (id) {
        $(table).find(":checked").filter("[value=" + id + "]").attr('checked', false);
    });
    return $.map($(table).find("input.row_checkbox:checked"), function (e) {
        return $(e).val();
    });
}


function handle_datasender_delete(table, allIds, all_selected){
    $("#note_for_delete_users").hide();

    var superusers_selected = get_user_names_from_selected_datasenders(table, allIds, all_selected);

    if (superusers_selected.length) {
        var users_list_for_html = "<li>" + superusers_selected.join("</li><li>") + "</li>";
        if (superusers_selected.length == allIds.length) { //Each DS selected is also User
            delete_all_ds_are_users_show_warning(users_list_for_html);
        } else { // A mix of DS and users
            $("#note_for_delete_users .users_list").html(users_list_for_html);
            $("#note_for_delete_users").show();
            warnThenDeleteDialogBox(allIds, all_selected, "reporter", this);
        }
    } else {
        warnThenDeleteDialogBox(allIds, all_selected, "reporter", this);
    }
}

function init_dialog_box_for_web_users() {
    var markup = "<tr><td>${short_name}</td><td>${name}</td><td style='width:150px;'>" +
        "${location}</td><td>" +
        "<input type='text' style='width:150px' class='ds-email ${hideInput}' ${input_field_disabled}/>" +
        "<label style='font-weight:inherit'>${email}</label>" +
        "</td></tr>";
    $.template("webUserTemplate", markup);

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
                    $("#datasender_table").dataTable().fnReloadAjax();
                    DW.flashMessage("Access to Web Submission has been given to your DataSenders")
                } else {
                    var html = "";
                    var i = 0;
                    for (i; i < json_data.errors.length; i = i + 1) {
                        var email_in_error = json_data.errors[i].split(' ')[3];
                        var error_message = gettext('User with email ') + email_in_error + gettext(' already exists');
                        html += "<tr><td>" + error_message + "</td></tr>";
                    }

                    var duplicate_entries = json_data.duplicate_entries;
                    var rep_ids = Object.keys(duplicate_entries);
                    var duplicate_emails = rep_ids.map(function (key) {
                        return json_data.duplicate_entries[key];
                    });
                    if (duplicate_emails.length != 0) {
                        error_message = gettext("You cannot use the same email address for multiple Data Senders. Revise the email address for the following users: ")+rep_ids.join(", ");
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
}

function init_dialog_box_for_datasender() {
    $("#datasender-popup").dialog({
        autoOpen: false,
        modal: true,
        zIndex: 1100,
        width: 700,
        beforeClose: function () {
            $('#action').removeAttr("data-selected-action");
            $('#web_user_error').hide();
        },
        close:function(){
            $("#datasender_table").dataTable().fnReloadAjax();
        }
    });

}

function init_dialog_box_for_group(){
    var allGroupsBlock = $("#all_groups_block");
    allGroupsBlock.dialog("destroy");
    allGroupsBlock.dialog({
        autoOpen: false,
        modal: true,
        title: gettext("Add to Groups"),
        zIndex: 1100,
        width: 'auto',
        dialogClass: 'all_groups_dialog',
        beforeClose: function () {
            $('#action').removeAttr("data-selected-action");
        },
        close:function(){
            $("#datasender_table").dataTable().fnReloadAjax();
        }
    });
    // Since the dialog is initialized on click of the menu item, we are hiding the dialog body.
    allGroupsBlock.removeClass("none");
}

function handle_datasender_edit(table, selectedIds) {
    var group = $("input[value=" + selectedIds[0] +"]").parent().parent().children().last().text();
    var popupHeader = group == 'contact'? gettext("Edit Contact") : gettext('Edit Datasender');
    $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css: { width: '275px'}});
    $.ajax({
        type: 'GET',
        url: '/entity/datasender/edit' + '/' + selectedIds[0].toLowerCase() + '/',
        success: function (response) {
            $("#datasender-popup").html(response) ;
            $("#datasender-popup").dialog('option','title', popupHeader).dialog("open");
            new DW.InitializeEditDataSender().init();
            $.unblockUI();

        }
    });
}
function register_datasender(table) {
    var project_id = $('#project_id').val();
    var modal_header = project_id ? gettext('Register a Datasender') : gettext('Add a Contact');

    $.ajax({
        type: 'GET',
        url:  '/entity/datasender/register',
        data:{'project_id':project_id},
        success: function (response) {
            $("#datasender-popup").html(response) ;
            $("#datasender-popup").dialog('option','title', modal_header).dialog("open");
            reporter_id_generation_action();
            updateShortCodeDisabledState();
            new DW.InitializeEditDataSender().init();
        }
    });
}

function populate_dialog_box_for_web_users(table, all_selected) {
    if (all_selected) {
        var total_records = table.fnSettings().fnRecordsDisplay();
        var current_page_size = $(table).find("input.row_checkbox:checked").length;
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
        data_sender.short_name = $($(row).children()[6]).html();
        data_sender.name = $($(row).children()[1]).html();
        data_sender.location = $($(row).children()[4]).html();
        data_sender.email = $($(row).children()[3]).html();
        data_sender.input_field_disabled = "disabled";
        if (!$.trim(data_sender.email)) {
            data_sender.input_field_disabled = "";
            data_sender.email = "";
        } else {
            data_sender.hideInput = "none";
        }

        data_sender_details.push(data_sender);
    });

    $('#web_user_table_body').html($.tmpl('webUserTemplate', data_sender_details));

    $("#web_user_block").dialog("open")
}

$(document).ready(function(){
   $("#change_ds_setting").dialog({
        title: gettext("People Authorized to Submit Data Using SMS"),
        modal: true,
        autoOpen: false,
        height: 260,
        width: 620,
        closeText: 'hide',
        close: function(){
            DW.vm.is_open_survey(initial_is_open_survey);
        }
      }
   );
    
   $("#change_ds_setting #cancel_ds_setting").on("click", function() {
       DW.trackEvent('datsender-group', 'cancel-datasender-group-dialog');
       $("#change_ds_setting").dialog("close");
       DW.vm.is_open_survey(initial_is_open_survey);
       return false;
   });

   $("#change_ds_setting #save_ds_setting").on("click", function(){
       $("#save_ds_setting").html(gettext('Saving...'));
       $("#save_ds_setting").removeClass('button');
       $("#save_ds_setting").addClass('disable_link disabled_yellow_submit_button ');
       DW.loading();
       var project_id = $('#project_id').val();
       var selected = $("#change_ds_setting input[name='ds_setting']:checked").val();
       $.ajax({url:'/project/change-group/',
               type:'POST',
               data: { 'project_id':project_id,
                       'selected':selected
               }
       }).done(function (json_response) {
           var response = $.parseJSON(json_response);

                if(selected == 'open'){
                    DW.trackEvent('datasender-group', 'updated-to-open-survey');
                }
                else{
                    DW.trackEvent('datasender-group', 'updated-to-restricted-survey');

                }

                if (response.success) {
                    window.location.href = "/project/registered_datasenders/" + project_id + "/";
                    $("#save_ds_setting").html(gettext('Save'));
                }
           }
       );
   });
});