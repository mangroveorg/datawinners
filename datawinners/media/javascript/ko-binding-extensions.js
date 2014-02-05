ko.bindingHandlers.sortable = {
    init: function(element, valueAccessor) {
        var list = valueAccessor();
        $(element).sortable({
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