ko.bindingHandlers.sortable = {
    init: function (element, valueAccessor) {
        var item_list = valueAccessor();
        $(element).sortable({
            cursor: "move",
            items: ".sort",
            update: function (event, ui) {
                var position = ui.item.index();
                var item = ko.dataFor(ui.item[0]);

                if (position >= 0) {
                    item_list.remove(item);
                    item_list.splice(position, 0, item);
                }
                ui.item.remove();
            }
        });
    }
};

ko.bindingHandlers.scrollToView = {
    update: function (element, valueAccessor) {
        observable = valueAccessor();
        if (observable()) {
            scrollFollow = element;
            if (scrollFollow) {
                scrollFollow.scrollTop = scrollFollow.scrollHeight - scrollFollow.clientHeight;
                observable(false);
            }
        }
    }
};

ko.bindingHandlers.scrollToElement = {
    update: function (element, valueAccessor) {
        var shouldShow = ko.utils.unwrapObservable(valueAccessor());
        if (shouldShow) {
            $('html, body').animate({scrollTop: $(element).offset().top}, 'slow')
        }
    }
};

ko.bindingHandlers.fadeVisible = {
    init: function (element, valueAccessor) {
        // Start visible/invisible according to initial value
        var shouldDisplay = ko.utils.unwrapObservable(valueAccessor());
        $(element).toggle(!!shouldDisplay); //converting shouldDisplay to boolean
    },
    update: function (element, valueAccessor) {
        // On update, fade in/out
        var shouldDisplay = ko.utils.unwrapObservable(valueAccessor());
        shouldDisplay ? $(element).fadeIn('fast') : $(element).fadeOut('fast');
    }
};


ko.bindingHandlers.accordion = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        var accessor = valueAccessor();
        var options = ko.toJS(accessor) || {};
        if(options.active == undefined)
            options.active = 100;

        $(element).accordion({
            autoHeight: false,
            collapsible: true,
            active: options.active,
            header: options.header,
            change: function(event, ui){
                var activatedSection = $(event.target).accordion('option', 'active');
                var activeObservable = accessor.active
                activeObservable && activeObservable(activatedSection);
            }
        });
    },
    update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        var accessor = valueAccessor();
        var options = ko.toJS(accessor) || {};
        if(options.active == undefined)
            options.active = 100;

        $(element).accordion('destroy').accordion({
            autoHeight: false,
            collapsible: true,
            active: options.active,
            header: options.header,
            change: function(event, ui){
                var activatedSection = $(event.target).accordion('option', 'active');
                var activeObservable = accessor.active
                activeObservable && activeObservable(activatedSection);
            }
        });
    }
};

ko.bindingHandlers.initializeTooltip = {
    init: function (element, valueAccessor) {
        $(element).tooltip({
            position: "top right",
            relative: true,
            opacity: 0.8,
            events: {
                def: "mouseover,mouseout",
                input: "focus,blur",
                widget: "focus mouseover,blur mouseout",
                tooltip: "click,click"
            }
        }).dynamic({ bottom: { direction: 'down', bounce: true } });
    }
};

ko.bindingHandlers.hidden = {
    update: function (element, valueAccessor) {
        var value = ko.utils.unwrapObservable(valueAccessor());
        ko.bindingHandlers.visible.update(element, function () {
            return !value;
        });
    }
};

ko.bindingHandlers.watermark = {
    init: function(element, valueAccessor, allBindingsAccessor) {
		var allBindings = allBindingsAccessor();
		var text, options;
		var watermark = allBindings.watermark;

		if (typeof watermark == "string"){
            text = watermark;
        }
		else{
			text = watermark.text;
//			options = watermark.options;
		}
        $(element).watermark(text);
    },
    update: function(element, valueAccessor){
        var value = valueAccessor();
        if(value.inputValue() != undefined && value.inputValue()!= "")
            $(element).prev("label").hide();
        else
            $(element).prev("label").show();
    }
};

ko.bindingHandlers.onoff = {

    init:function(element, valueAccessor) {
        var isOn = ko.unwrap(valueAccessor());
        var ele = $(element);
        if (isOn){
            ele.addClass('onoffswitch-checked');
        }
        ele.on('click', function(e){
            if (!ele[0].hasAttribute('disabled')){
                var boolVal = ko.unwrap(valueAccessor());
                valueAccessor()(!boolVal);
            }
            e.preventDefault();
        });
    },

    update: function(element, valueAccessor, allBindingsAccessor, context) {
        var isOn = ko.unwrap(valueAccessor());
        if(!isOn){
            $(element).removeClass('onoffswitch-checked');
        }
        else{
            $(element).addClass('onoffswitch-checked');
        }
    }
};

ko.bindingHandlers.messageEditor = {

    init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
        var obj = valueAccessor();
        $(element).TextNTags({
            plainText: obj.message(),
            contentChangedHandler: function(){
                obj.message($(element).TextNTags('getText'));
                obj.count($(element).TextNTags('characterCount'));
            }
        });
    }

};

ko.bindingHandlers.dialog = {
        init: function(element, valueAccessor, allBindingsAccessor) {
            var options = ko.utils.unwrapObservable(valueAccessor()) || {};
            setTimeout(function() {
                options.close = function() {
                    allBindingsAccessor().dialogVisible(false);
                };
                options.title = gettext(options.title);
                $(element).dialog(options);
            }, 0);

             ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
                 $(element).dialog("destroy");
             });
        },
        update: function(element, valueAccessor, allBindingsAccessor) {
            var shouldBeOpen = ko.utils.unwrapObservable(allBindingsAccessor().dialogVisible),
                dialog_content = ko.utils.unwrapObservable(allBindingsAccessor().dialogContent)||" ",
                $el = $(element),
                dialog = $el.data("uiDialog") || $el.data("dialog");

            if (dialog) {
                $el.html(dialog_content);
                $el.dialog(shouldBeOpen ? "open" : "close");
            }
        }
};