DW.action_dropdown = function (kwargs) {
    var defaults = {
        trigger: "button.action",
        checkbox_locator:"#subject_table input:checkbox",
        data_locator:"#action",
        none_selected_locator:"#none-selected",
        many_selected_msg: gettext("Select 1 Data Sender only"),
        check_single_checked_locator: "#subject_table tbody input:checkbox[checked=checked]",
        no_cb_checked_locator: "#subject_table input:checkbox[checked=checked]",
        edit_link_locator: "#edit",
        container: document,
        checkall: "#checkall-checkbox"
    };

    this.options = $.extend(true, defaults, kwargs);
    this._init();
};

DW.action_dropdown.prototype = {
    _init: function(){
        var opts = this.options;
        this.checkbox_locator = opts.checkbox_locator;
        this.data_locator = opts.data_locator;
        this.none_selected_locator = opts.none_selected_locator;
        this.many_selected_msg = opts.many_selected_msg;
        this.check_single_checked_locator = opts.check_single_checked_locator;
        this.action_enabled = false;
        this.no_cb_checked_locator = opts.no_cb_checked_locator;
        this.trigger = opts.trigger;
        this.edit_link_locator = opts.edit_link_locator;
        this.container = opts.container;
        this.checkall = opts.checkall;
        this.is_on_trial = false;

        this.init_dropdown = function(){
            var edit_link = $(this.edit_link_locator, this.container);
            if (edit_link.parent().hasClass("on_trial")) {
                edit_link.removeAttr("title");
                edit_link.parent().addClass("disabled");
                this.is_on_trial = true;
            }

            $(this.container).on('click', this.checkbox_locator, {self:this}, function(event){
                var self = event.data.self;
                var checked = $(this).attr("checked") == "checked";
                if (checked && !self.action_enabled) {
                    self.init_action_dropdown();
                } else if (!checked && self.action_enabled &&
                    ($(self.no_cb_checked_locator, self.container).length == 0 || $(self.checkall, self.container)[0] == $(this)[0])) {
                    self.deactivate_action();
                }

                if (self.action_enabled && !self.is_on_trial) {
                    self.update_edit_action();
                }
            });
            
            this.deactivate_action();
        };

        this.init_action_dropdown = function(){
            $(this.trigger, this.container).dropdown("detach");
            $(this.trigger, this.container).dropdown("attach", [this.data_locator]);
            this.action_enabled = true;
        };

        this.deactivate_action = function(){
            $(this.trigger, this.container).dropdown("detach");
            $(this.trigger, this.container).dropdown("attach", [this.none_selected_locator]);
            this.action_enabled = false;
        };

        this.update_edit_action = function(){
            var link = $(this.edit_link_locator, this.container);
            if ($(this.check_single_checked_locator, this.container).length == 0) {
                this.deactivate_action();
                return true;
            }
            
            if ($(this.check_single_checked_locator, this.container).length > 1){
                link.parent().addClass("disabled");
                link.attr("disabled", "disabled");
                link.attr("title", this.many_selected_msg);
            } else {
                link.parent().removeClass("disabled");
                link.removeAttr("title");
            }
        };

        this.uncheck_all = function(){
            $(this.checkbox_locator).removeAttr('checked');
        }

        this.init_dropdown();
    }
};