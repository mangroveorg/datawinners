$(document).ready(function() {
    $("#error_table").hide();

    var uploader = new qq.FileUploader({
        // pass the dom node (ex. $(selector)[0] for jQuery users)
        element: document.getElementById('file_uploader'),
        // path to server-side upload script
        action: window.location.pathname,
        onComplete: function(id, fileName, responseJSON) {
            $('#message').remove();
            $('#error_tbody').html('');
            $("#error_table").hide();
            $("#subject_table tbody").html('');
            $.each(responseJSON.all_data, function(index, element) {
                $("#subject_table tbody").append("<tr>" +
                        "<td><input type='checkbox' id='" + element.short_name + "' value='" + element.short_name + "'/></td>" +
                        "<td>" + element.short_name + "</td>" +
                        "<td>" + element.name + "</td>" +
                        "<td>" + element.type + "</td>" +
                        "<td>" + element.location + "</td>" +
                        "<td>" + element.geocode + "</td>" +
                        "<td>" + element.mobile_number + "</td>" +
                        "<td>" + element.projects + "</td>" +
                        "<td>" + element.email + "</td></tr>")
            });
            if (responseJSON.success == true) {
                $('<div id="message" class="success_message success-message-box">' + responseJSON.message + '</div>').insertAfter($('#file-uploader'));

            }
            else {
                $('#error_tbody').html('');
//                $("#error_table").show();
                if (responseJSON.error_message) {
                    $('<div id="message" class="error_message message-box">' + responseJSON.error_message + '</div>').insertAfter($('#file-uploader'));
                }
                else {
                    $('<div id="message" class="error_message message-box">' + responseJSON.message + '</div>').insertAfter($('#file-uploader'));
                }
                if (responseJSON.failure_imports > 0) {
                    $("#error_table").show();
                }
                $.each(responseJSON.failure_imports, function(index, element) {
                    $("#error_table table tbody").append("<tr><td>" + element.row_num + "</td><td>" + JSON.stringify(element.row) + "</td><td>"
                            + element.error + "</td></tr>")
                });
                $("#error_table").show();
            }

        }
    });


    function updateIds() {
        var allIds = [];
        $('#all_data_senders :checked').each(function() {
            allIds.push($(this).val());
        });
        return allIds;
    }

    $("#all_project_block").dialog({
        autoOpen: false,
        modal: true,
        title: 'Select Projects',
        zIndex:1100,
        beforeClose: function() {
            $('#action').val('');
        }
    });
    $("#web_user_block").dialog({
        autoOpen: false,
        modal: true,
        title: gettext('Give Web Submission Access'),
        zIndex:1100,
        width: 900,
        beforeClose: function() {
            $('#action').val('');
            $('#web_user_error').hide();
        }
    });


    $("#all_project_block .cancel_link").bind("click", function() {
        $("#all_project_block").dialog("close");
    });

    $("#web_user_block .cancel_link").bind("click", function() {
        $("#web_user_block").dialog("close");
    });

    $("#all_project_block .button").bind("click", function() {
        $('#error').remove();
        var allIds = updateIds();
        var projects = [];
        $('#all_project_block :checked').each(function() {
            projects.push($(this).val());
        });
        if (projects.length == 0) {
            $('<div class="message-box" id="error">' + gettext("Please select atleast 1 Project") + '</div>').insertBefore($("#all_projects"))
        }
        else {
            var url = '/entity/' + $('#action').val() + '/'
            $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>' ,css: { width:'275px', zIndex:1000000}});
            $.post(url,
                    {'ids':allIds.join(';'),'project_id':projects.join(';')}
            ).success(function(data) {
                        window.location.href = data;
                    });
        }
    });

    $('#action').change(function() {
        var allIds = updateIds();
        $('#error').remove();
        if (allIds.length == 0) {
            $('#web-access-success').remove();
            $('<div class="message-box" id="error">' + gettext('Please select atleast 1 data sender') + '</div>').insertAfter($(this));
            $('#project').val('');
            $(this).val("");
            return;
        }
        var action = $(this).val();
        if(action=='makewebuser'){
            populate_dialog_box_for_web_users();
            return false;
        }else{
            $("#all_project_block").dialog("open");
        }
    });

    function populate_dialog_box_for_web_users() {
        var data_sender_details = [];
        $('#all_data_senders :checked').each(function() {
            var row = $(this).parent().parent();
            var data_sender = {};
            data_sender.short_name = $($(row).children()[1]).html();
            data_sender.name = $($(row).children()[2]).html();
            data_sender.location = $($(row).children()[4]).html();
            data_sender.contactInformation = $($(row).children()[6]).html();
            data_sender.email = $($(row).children()[8]).html();
            data_sender.input_field_disabled = "disabled";
            if(data_sender.email.trim() == "--"){
                data_sender.input_field_disabled = "";
                data_sender.email = "";
            }
            data_sender_details.push(data_sender);
        });
        $('#web_user_table_body').html($.tmpl('webUserTemplate', data_sender_details));
        $("#web_user_block").dialog("open");
    }

    $('#web_user_button').click(function() {
        $('#web_user_error').hide();
        var post_data = [];
        var should_post = true;
        $('input:enabled.ds-email').each(function() {
            var email = $(this).val();
            var emailRegEx = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i;
            if (email.trim() == "") {
                $('#web_user_error').show();
                $('#web_user_error').html(gettext('Emails are mandatory'));
                should_post = false;
                return false;
            }
            if(email.trim().search(emailRegEx) == -1){
                $('#web_user_error').show();
                $('#web_user_error').html(email + gettext(": is not a valid email"));
                should_post = false;
                return false;
            }
            var reporter_id = $($(this).parent().parent().children()[0]).html();
            post_data.push({email: email, reporter_id: reporter_id});
        });
        if(!should_post || post_data.length == 0){
            return;
        }
        $.blockUI({ message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>' ,css: { width:'275px', zIndex:1000000}});
        $.post('/entity/webuser/create', {post_data: JSON.stringify(post_data)},
                function(response) {
                    var json_data = JSON.parse(response);
                    if (json_data.success) {
                        $("#web_user_block").dialog("close");
                        redirect_url = location.href;
                        if(redirect_url.indexOf('?web=1') == -1) {
                            redirect_url = redirect_url + '?web=1';
                        }
                        window.location.href = redirect_url
                    } else {
                        $.unblockUI();
                        var html = "";
                        for (var i = 0; i < json_data.errors.length; i++) {
                            console.log(json_data);
                            var email_in_error = json_data.errors[i].split(' ')[3];
                            var error_message = gettext('User with email ') + email_in_error + gettext(' already exists')
                            html += "<tr><td>" + error_message + "</td></tr>";
                        }
                        $('#web_user_error').html(html);
                        $('#web_user_error').show();
                    }

                });
        return false;
    });

    var markup = "<tr><td>${short_name}</td><td>${name}</td><td style='width:150px;'>${location}</td><td>${contactInformation}</td><td><input type='text' style='width:150px' class='ds-email' value='${email}' ${input_field_disabled}/></td></tr>"
    $.template("webUserTemplate", markup);
});