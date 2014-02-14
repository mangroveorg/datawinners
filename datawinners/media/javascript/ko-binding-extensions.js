ko.bindingHandlers.sortable = {
    init: function(element, valueAccessor) {
        var item_list = valueAccessor();
        $(element).sortable({
            cursor: "move",
            items: ".sort",
            update: function(event, ui) {
                var position = ui.item.index();
                var item = ko.dataFor(ui.item[0]);

                if (item_list()[position].is_entity_question())
                    return false;

                if (position >= 0) {
                    item_list.remove(item);
                    item_list.splice(position, 0, item);
                }
                ui.item.remove();
            }
        });
    },
//    update: function(element, valueAccessor) {
//        $(element).sortable({
//            items: ".sort"
//        })
//    }
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