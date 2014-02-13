ko.bindingHandlers.sortable = {
    init: function(element, valueAccessor) {
        var list = valueAccessor();
        $(element).sortable({
            cursor: "move",
            cancel: ".ignore_sort",
            update: function(event, ui) {
                var position = ui.item.index();
                var item = ko.dataFor(ui.item[0]);
                if (position >= 0) {
                    list.remove(item);
                    list.splice(position, 0, item);
                }
                ui.item.remove();
            }
        });

    }
};

ko.bindingHandlers.scrollToView = {
    update: function(element, valueAccessor) {
        observable = valueAccessor();
        if(observable()){
            scrollFollow = element;
             if (scrollFollow) {
                scrollFollow.scrollTop = scrollFollow.scrollHeight - scrollFollow.clientHeight;
                observable(false);
             }
        }
    }
}