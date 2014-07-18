var viewModel = function(initial_value){
    this.is_open_datasender = ko.observable(initial_value);
    this.ds_setting_description = ko.computed(function(){
        if (this.is_open_datasender() == '1')
            return gettext("Everyone");
        else
            return gettext("Only registered Datasenders");
    }, this);
}

$(document).ready(function () {
    DW.vm = new viewModel(initial_is_open_datasender);
    ko.applyBindings(DW.vm);
});