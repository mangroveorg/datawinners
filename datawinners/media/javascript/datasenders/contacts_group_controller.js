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

    //self.showUniqueIdTypeList = ko.computed(function(){
    //    return self.uniqueIdTypes().length == 0;
    //}, self);


    //self.selectUniqueIdType = function (uniqueIdType) {
    //    ProjectQuestionnaireViewModel.prototype.selectedQuestion().uniqueIdType(uniqueIdType);
    //    self.isUniqueIdTypeVisible(false);
    //    _clearNewUniqueIdError();
    //};

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
        selected_group = new_group.name;
        $("#datasender_table").dataTable().fnReloadAjax()
    });

    //function _clearNewGroupError() {
    //    self.newGroup("");
    //    self.newGroup.clearError();
    //}

    //function _resetUniqueIdTypeContentState() {
    //    _clearNewGroupError();
    //    self.isUniqueIdTypeVisible(false);
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
}

$(document).ready(function() {
    _initializeViewModel();
    var groupPanel = $("#group_panel");
    ko.applyBindings(groupViewModel, groupPanel[0]);
});