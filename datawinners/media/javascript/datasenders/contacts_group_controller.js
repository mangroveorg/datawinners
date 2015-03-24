DW.group = function(group){
    var defaults = {
        name: ''
    };
    this.options = $.extend(true, defaults, group);
    this._init();
};
DW.group.prototype = {
    _init:function(){
        var g = this.options;
        this.name = g.name;
    }
};
function ContactsGroupViewModel() {
    var self = this;
    self.groups = ko.observableArray();

    //self.newGroup = DW.ko.createValidatableObservable();
    //self.groupButtonText = ko.observable(gettext("Add"));

    //self.addNewGroup = function () {
    //    var newGroup = self.newGroup();
    //    self.groupButtonText(gettext("Adding..."));
    //    $.post('/entity/group/create', {group_type_regex: newGroup})
    //        .done(function (responseString) {
    //            self.groupButtonText(gettext('Add'));
    //            var response = $.parseJSON(responseString);
    //            if (response.success) {
    //                var array = self.groups();
    //                array.push(newGroup);
    //                array.sort();
    //                self.newGroup.clearError();
    //                self.groups.valueHasMutated();
    //                //self.selectUniqueIdType(newUniqueIdType);
    //            }
    //            else {
    //                self.newGroup.setError(response.message);
    //            }
    //        });
    //};
    self.selectedGroup = ko.observable();
    self.changeSelectedGroup = function(group){
        self.selectedGroup(group);
        //$(this).addClass("group_selected");
    };
    self.selectedGroup.subscribe(function(new_group){
        selected_group = new_group.name; //used to send group name as filter
        $("#datasender_table").dataTable().fnReloadAjax()
    });

    //function _clearNewGroupError() {
    //    self.newGroup("");
    //    self.newGroup.clearError();
    //}

    self.loadGroup = function (group) {
        self.groups.push(group);
    };


}
function _initializeViewModel(){
    window.groupViewModel = new ContactsGroupViewModel();
    $(existing_groups).each(function(index, group){
            groupViewModel.loadGroup(new DW.group(group));
    });
    //groupViewModel.changeSelectedGroup(groupViewModel.groups()[0]);
}

$(document).ready(function() {
    _initializeViewModel();
    var groupPanel = $("#group_panel");
    ko.applyBindings(groupViewModel, groupPanel[0]);
    //groupViewModel.changeSelectedGroup(groupViewModel.groups()[0]);
});