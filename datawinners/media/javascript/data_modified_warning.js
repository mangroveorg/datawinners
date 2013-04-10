DW.data_submission = function (kwargs) {
    var defaults = {
        bind_no_button_in_dialog:function () {
            $("#cancel_submission_warning_message .no_button").bind('click', function () {
                $("#cancel_submission_warning_message").dialog("close");
            })
        },

        bind_yes_button_in_dialog:function () {
            var that = this;
            $("#cancel_submission_warning_message .yes_button").bind('click', function () {
                that.redirect();
            })
        },

        bind_cancel_link_in_dialog:function () {
            return false;
        }
    };

    this.options = $.extend(true, defaults, kwargs);
    this._init();
}

DW.data_submission.prototype = {
    _init:function () {
        var opts = this.options;
        this.bind_no_button_in_dialog = opts.bind_no_button_in_dialog;
        this.bind_yes_button_in_dialog = opts.bind_yes_button_in_dialog;
        this.bind_cancel_link_in_dialog = opts.bind_cancel_link_in_dialog;
        this.cancel_id = "#cancel";
        this.init();
    },

    init_warning_dialog:function () {
        $("#cancel_submission_warning_message").dialog({
            title:gettext("Warning"),
            modal:true,
            autoOpen:false,
            height:160,
            width:400,
            closeText:'hide'
        });
    },

    initial_form_values:function () {
        $('form :input').each(function () {
            $(this).data('initialValue', $(this).val());
        });
    },

    bind_cancel_link:function () {
        var that = this;
        $("a[href]:visible").not(".delete_project, .sms_tester, .activate_project").bind('click', function () {
            that.redirect_url = $(this).attr("href");
            if (that.is_form_changed() || $(".message-box").length || $(".errorlist li").length) {
                $("#cancel_submission_warning_message").dialog("open");
                return false;
            } else
                that.redirect();
        });
    },

    is_form_changed:function () {
        var is_changed = false;
        $('form :input').each(function () {
            if ($(this).data("initialValue") !== $(this).val()) {
                is_changed = true;
            }
        });
        return is_changed;
    },

    redirect: function() {
        window.location.href = this.redirect_url;
    },

    init: function () {
        this.init_warning_dialog();
        this.initial_form_values();
        this.bind_cancel_link();
        this.bind_no_button_in_dialog();
        this.bind_yes_button_in_dialog();
        this.bind_cancel_link_in_dialog();
    },

    refresh: function () {
        this.init();
    }
};