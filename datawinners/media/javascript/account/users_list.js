$(document).ready(function () {
    $('#error').css("display", "none");
    $("#check_all_users").bind("click", function () {
        $(".user_entry").attr("checked", $(this).attr("checked"));
    });

    $(".action").each(function (i, action) {
        $(action).bind("change", function () {
            var ids = updateIds();
            $("#error").css("display", "none");
            var action = $(this).val();
            if (ids.length == 0) {
                $("#error").css("display", "block");
                $(this).val("");
                return;
            }
            if (action == "delete") {
                $("#delete_user_warning_dialog").dialog("open");
            }
        });
    });

    function updateIds() {
        var allIds = [];
        $('.user_entry:checked').each(function () {
            allIds.push($(this).val());
        });
        return allIds;
    }

    var kwargs = {container:"#delete_user_warning_dialog",
        continue_handler:function () {
            var allIds = updateIds();
            var post_data = {'all_ids':allIds.join(';')}
            $.blockUI({ message:'<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>', css:{ width:'275px'}});
            $.post("/account/users/delete/", post_data,
                function (json_response) {
                    var response = $.parseJSON(json_response);
                    if (response.success) {
                        window.location.href = window.location.href;
                    }
                }
            );
            return false;
        },
        title:gettext("Your User(s) will be deleted"),
        cancel_handler:function () {
            $("#action").val("");
        },
        height:150,
        width:550
    }

    DW.delete_user_warning_dialog = new DW.warning_dialog(kwargs);
});
