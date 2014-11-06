$(document).ready(function () {
    $('#error').css("display", "none");
    $("#check_all_type").bind("click", function () {
        $(".subject_type_entry").attr("checked", $(this).attr("checked") == "checked");
    });

    $(".subject_type_entry").bind("click", function(){
        var checked = $(".subject_type_entry:checked").length == $(".subject_type_entry").length;
        $("#check_all_type").attr("checked", checked)
    });

    $("#action li a").each(function (i, action) {
        $(action).bind("click", function () {
            var ids = updateIds();
            $("#error").css("display", "none");
            var action = $(this).attr('action-dropdown');
            if (ids.length == 0) {
                $("#error").css("display", "block");
                $(this).val("");
                return;
            }
            if (action == "delete") {
                compt = 0;
                warning_title = [];
                has_questionnaires = false;
                content = gettext("If you want to delete the Identification Number Type <b>");
                subject_list = [];
                $("#delete_subject_type_associated_questionnaires_warning_dialog .warning_message").html("");
                content = gettext("If you want to delete the Identification Number Type <b>");
                $('.list_header').each(function() {
                    line = this;
                    message = "";
                    $(this).find(".subject_type_entry:checked").each(function(){
                        if($(line).find(".questionnaires").text()){
                            has_questionnaires = true;
                            message = gettext("The following Questionnaire(s) are collecting data about <b>") + $(line).find(".header").html()+ "</b><ul class='bulleted'>";
                            $(line).find(".questionnaires span").each(function(){
                                message = message + "<li style='margin-left:15px;'>"+$(this).html()+"</li>";

                            });
                            message = message + "</ul></br>";
                            list = $(line).find(".questionnaires");
                            subject_list.push($(line).find(".header").html());
                            content = content + subject_list.join("</b> and <b>") + gettext("</b>, you need to remove these questions using ") + interpolate(gettext("<b> %(entity_type)s </b> as a identification Number first"), {entity_type: $(line).find(".header").html()}, true);
                        }

                    });
                    $("#delete_subject_type_associated_questionnaires_warning_dialog .warning_message").append(message);
                });
                if(has_questionnaires)
                {
                    $("#delete_subject_type_associated_questionnaires_warning_dialog .warning_message").append(content);
                    $("#delete_subject_type_associated_questionnaires_warning_dialog").dialog("open");
                }
                else{
                    $("#delete_subject_type_warning_dialog").dialog("open");
                    var compt = 1;
                    $('#delete_subject_type_warning_dialog span.delete_subjects_list_label').html("");
                    $('.subject_type_entry:checked').each(function() {
                        var value = $(this).attr('value').substring(0,1).toUpperCase() + $(this).attr('value').substring(1, $(this).attr('value').length);
                        if(compt == $('.subject_type_entry:checked').length)
                        {
                            if($('.subject_type_entry:checked').length != 1)
                                $('#delete_subject_type_warning_dialog span.delete_subjects_list_label').append(" and ");
                        }
                        else
                            if(compt != 1)
                                $('#delete_subject_type_warning_dialog span.delete_subjects_list_label').append(", ");

                        $('#delete_subject_type_warning_dialog span.delete_subjects_list_label').append(value);
                        compt++;
                    });
                }
            }
        });
    });

    function updateIds() {
        var allIds = [];
        $('.subject_type_entry:checked').each(function () {
            allIds.push($(this).val());
        });
        return allIds;
    }

    var kwargs = {container:"#delete_subject_type_warning_dialog",
        continue_handler:function () {
            var allIds = updateIds();
            var post_data = {'all_ids':allIds.join(';')};
            $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
            $.post("/entity/subject/delete_types/", post_data,
                function (json_response) {
                    var response = $.parseJSON(json_response);
                    if (response.success) {
                        window.location.href = "/entity/subjects";
                    }
                }
            );
            return false;
        },
        title:gettext("Delete the Identification Number Type"),
        cancel_handler:function () {
            $(".action").val("");
        },
        height:"auto",
        width:550
    }
    var xwargs = {container:"#delete_subject_type_associated_questionnaires_warning_dialog",
            continue_handler:function () {
                $(".action").val("");
            },
            title:gettext("Delete Associated Questions First"),
            height:"auto",
            width:550
        }


    DW.delete_subject_type_warning_dialog = new DW.warning_dialog(kwargs);
    DW.delete_subject_type_associated_questionnaires_warning_dialog = new DW.warning_dialog(xwargs);

    var opts = {
        checkbox_locator:".all_subject_type_table input:checkbox",
        data_locator:"#action",
        none_selected_locator:"#none-selected",
        check_single_checked_locator:".all_subject_type_table input:checkbox[checked=checked]",
        no_cb_checked_locator:".all_subject_type_table input:checkbox[checked=checked]",
        checkall:"#check_all_type"
    }
    var subject_type_action_dropdown = new DW.action_dropdown(opts);
});
