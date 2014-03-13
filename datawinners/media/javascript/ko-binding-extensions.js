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
        $(element).toggle(!!shouldDisplay);
    },
    update: function (element, valueAccessor) {
        // On update, fade in/out
        var shouldDisplay = ko.utils.unwrapObservable(valueAccessor());
        shouldDisplay ? $(element).fadeIn('fast') : $(element).fadeOut('fast');
    }
};


ko.bindingHandlers.accordion = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        ko.bindingHandlers.foreach.init(element, valueAccessor, allBindings, viewModel, bindingContext);
        $(element).accordion({
            autoHeight: false,
            collapsible: true,
            active: 100
        });
    },
    update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        ko.bindingHandlers.foreach.update(element, valueAccessor, allBindings, viewModel, bindingContext);
        $(element).accordion('destroy').accordion({
            autoHeight: false,
            collapsible: true,
            active: 100
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

ko.bindingHandlers.buttonVisible = {
    init: function (element, valueAccessor) {
        $(element).hide();
        var accordionElement = valueAccessor().accordionElement;
        $(accordionElement).on('accordionchangestart', function () {
            var activatedAccordion = $(accordionElement).accordion('option', 'active');
            $(element).toggle(activatedAccordion !== false && activatedAccordion == 0);
        })
    },
    update: function (element, valueAccessor) {
        var selectedTemplateId = valueAccessor().observable;
        $(element).toggle(selectedTemplateId() != null);
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