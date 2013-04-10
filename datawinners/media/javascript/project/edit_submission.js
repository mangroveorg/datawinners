$(document).ready(function(){
    var options = {
        bind_cancel_link_in_dialog:function () {
            $("#cancel_submission_warning_message #cancel_leave").bind('click', function () {
                $("#cancel_submission_warning_message").dialog("close");
            })
        },

        bind_yes_button_in_dialog:function () {
            $("#cancel_submission_warning_message .yes_button").bind('click', {self:this}, function (event){
                var self = event.data.self;
                $("#redirect_url").val(self.redirect_url);
                $("form:first").trigger("submit");
            })
        },

        bind_no_button_in_dialog:function () {
            var that = this;
            $("#cancel_submission_warning_message .no_button").bind('click', function () {
                that.redirect();
            })
        }
    };

    DW.edit_submission_modified_data_handler = new DW.data_submission(options);
});
