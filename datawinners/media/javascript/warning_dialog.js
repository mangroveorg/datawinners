//For ie
DW.hide_dialog_overlay = function () {
    $('.ui-widget-overlay').hide();
}

DW.show_dialog_overlay = function () {
    $('.ui-widget-overlay').show();
}

DW.warning_dialog = function (kwargs) {
    var defaults = {
        width:650,
        is_continue:false,
        title:gettext("Warning"),
        continue_handler:function () {
            return false;
        },
        cancel_handler:function () {
            return false;
        }
    };

    this.options = $.extend(true, defaults, kwargs);
    this._init();
}

DW.warning_dialog.prototype = {
    _init:function () {
        var o = this.options;
        this.container = o.container;
        this.length = o.length;
        this.height = o.height;
        this.width = o.width;
        this.is_continue = o.is_continue;
        this.title = o.title;
        this.init_buttons = function () {
            if (typeof(this.options.confirm_button) == "undefined") {
                this.confirm_button = this.container + " .yes_button";
            } else {
                this.confirm_button = this.options.confirm_button;
            }
            if (typeof(this.options.cancel_button) == "undefined") {
                this.cancel_button = this.container + " .no_button";
            } else {
                this.cancel_button = this.options.cancel_button;
            }
        }
        this.not_confirm_button = o.container + " .no_button";
        this.continue_handler = o.continue_handler;
        this.cancel_handler = o.cancel_handler;
        this.init_dialog = function () {
            $(this.container).dialog({
                title:this.title,
                modal:true,
                autoOpen:false,
                height:this.height,
                width:this.width
            });
        }
        this.show_warning = function () {
            $(this.container).dialog("open");
            DW.show_dialog_overlay();
            this.is_continue = false;
        }
        this.close_dialog = function () {
            $(this.container).dialog("close");
        }
        this.bind_continue = function () {
            $(this.confirm_button).unbind().bind("click", {self:this}, function (event) {
                var self = event.data.self;
                self.is_continue = true;
                self.continue_handler();
                self.close_dialog();
            })
        }
        this.bind_cancel = function () {
            var cancel_sensors = new Array($(".ui-dialog-titlebar-close", $(this.container).parent()), $(this.cancel_button));
            var dialog = this;
            $.each(cancel_sensors, function( index, element){
                element.unbind().bind("click", {self:dialog}, function (event) {
                    var self = event.data.self;
                    self.is_continue = false;
                    self.cancel_handler();
                    self.close_dialog();
                })
            })
        }
        this.init = function () {
            this.init_dialog();
            this.init_buttons();
            this.bind_continue();
            this.bind_cancel();
        }
        this.init();
    }
}
