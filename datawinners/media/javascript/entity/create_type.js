$(document).ready(function () {
    $("#add_subject_type").accordion({collapsible: true, autoHeight: false, active: 2});

    $("#add_new_subject_type").live("click", function () {
        $("#type_message").html('');
        $("#type_message").removeClass("message-box");
        $("#id_entity_type_text").val("");
        if ($("#subjects_create_type").length) {
            $("#subjects_create_type").dialog("open");
        } else {
            $("#add_subject_type_content").removeClass("none");
        }
    });

    function should_append(options, new_type) {
        var i = 0;
        for (i; i < options.length; i = i + 1) {
            if (new_type == options[i].value) {
                return false;
            }
        }
        return true;
    }

    $("#add_type").live("click", function () {
        $("#type_message").html("<span class='ajax_loader_small'></span>");
        var new_type = $("#id_entity_type_text").val().toLowerCase();
        var referer = 'project';
        if ($("#subjects_create_type").length) {
            referer = 'subject';
        }
        $.post("/entity/type/create/", { entity_type_regex: new_type, referer: referer},
            function (response) {
                var data = JSON.parse(response);
                if (data.success) {
                    if ($("#subjects_create_type").length) {
                        $("#subjects_create_type").dialog("close");
                        window.location.replace("/entity/subjects/");
                    } else {
                        var options = $("#id_entity_type>option").map(function () {
                            return $(this).val();
                        });
                        if (should_append(options, new_type)) {
                            $("#id_entity_type").prepend($('<option></option>').val(new_type).html(new_type));
                        }
                        $("#id_entity_type").prop('selectedIndex', 0);
                        $('#id_entity_type').trigger('change');
                        $("#add_subject_type").accordion({collapsible: true, autoHeight: false, active: 2});
                        $("#id_entity_type_text").val("");
                    }
                    $("#type_message").html('');
                    $("#type_message").removeClass("message-box");
                } else {
                    $("#type_message").html(data.message);
                    $("#type_message").addClass("message-box");
                }
            });
    });

    $("#read_more").dialog({
        title: gettext("Read More"),
        modal: true,
        autoOpen: false,
        width: 800
    });

    $('#help_icon_for_add_subject, #add_subject_read_more').click(function () {
        $("#read_more").dialog("open");
        return false;
    });

    $("#subjects_create_type").dialog({
        title: gettext("Add a New Identification Number Type"),
        modal: true,
        autoOpen: false,
        width: 500,
        height: 300
    });

    $("#cancel_add_type").click(function () {
        $("#subjects_create_type").dialog("close");
    });
});
