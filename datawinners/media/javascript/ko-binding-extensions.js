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

ko.bindingHandlers.errorVisible = {
    update: function (element, valueAccessor) {
        var observable = valueAccessor();
        var shouldShow = ko.unwrap(observable);
        if (shouldShow && shouldShow.length > 0) {
            $('html, body').animate({scrollTop: $(element).offset().top}, 'slow')
        }
    }
};

ko.bindingHandlers.initializeAccordion = {
    init: function (element, valueAccessor) {
        $(element).accordion({
            header: valueAccessor().accordionHeader,
            autoHeight: false,
            collapsible: true,
            active: 100
        });
    }
};

ko.bindingHandlers.buttonVisible = {
  init: function(element, valueAccessor){
      $(element).hide();
      var accordionElement = valueAccessor().accordionElement;
      $(accordionElement).on('accordionchangestart', function(){
          var isAnyAccordionActive = $(accordionElement).accordion('option', 'active');
          $(element).toggle(isAnyAccordionActive !== false);
      })
  }
};

