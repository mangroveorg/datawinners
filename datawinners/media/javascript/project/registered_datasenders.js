var viewModel = function(initial_value){
    this.is_open_survey = ko.observable(initial_value);
    this.ds_setting_description = ko.computed(function(){
        if (this.is_open_survey() == '1')
            return gettext("Everyone - Anyone with a simple phone can submit data.");
        else
            return gettext("Only Registered People - Data Senders must be registered first before submitting data.");
    }, this);
}

$(document).ready(function () {
    DW.vm = new viewModel(initial_is_open_survey);
    ko.applyBindings(DW.vm);
});
