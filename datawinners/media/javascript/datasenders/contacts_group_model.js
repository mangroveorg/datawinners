DW.group = function (group) {
    var self = this;

    var defaults = {
        name: '',
        code:'',
        isEditable: true
    };
    this.options = $.extend(true, defaults, group);
    this.deleteGroup = function(){
        DW.loading();
        return $.post(delete_group_url, {
            'group_name': self.name(),
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        });

    };

    this.updateName = function(newName){
      self.name(newName);
      self.code(newName);
    };

    this._init();
};
DW.group.prototype = {
    _init: function () {
        var g = this.options;
        this.name = ko.observable(g.name);
        this.newName = ko.observable(g.name);
        this.code = ko.observable(g.name);
        this.isEditMode = ko.observable(false);
        this.isEditable = ko.observable(g.isEditable);
    }
};
function ContactsGroupViewModel() {
    var self = this;
    self.groups = ko.observableArray();
    self.groupButtonText = ko.observable(gettext("Add"));
    self.newGroupName = ko.observable('');
    self.newGroupError = ko.observable('');
    self.newGroupValid = ko.observable(true);
    self.selectedGroup = ko.observable();
    self.isOpen = ko.observable(false);
    self.disable_button = ko.observable(false);
    self.disable_attr = ko.observable(null);
    self.addGroupDialogContent = ko.observable($('#add_group_dialog_content').html());

    self.disable_add_button = function() {
        self.groupButtonText(gettext("Adding..."));
        self.disable_attr('disabled');
        self.disable_button(true);
    };
    self.enable_add_button = function() {
        self.groupButtonText(gettext("Add"));
        self.disable_attr(null);
        self.disable_button(false);
    };

    self.renameGroup = function(group){
        group.isEditMode(true);
    };

    self.undoEdit = function(group){
        group.isEditMode(false);
    };

    self.confirmGroupRename = function(group){
        DW.loading();
        $.post(group_rename_url, {
            group_name: group.name(),
            new_group_name: group.newName(),
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        }).done(function (response){
            if(response.success){
                group.updateName(group.newName());
                self.changeSelectedGroup(group);
                group.isEditMode(false);
            }
            else{
                alert("Rename failed");
            }
        }).error(function(){
            console.log("Rename threw an exception");
        });
    };

    self.addNewGroup = function () {
        var newGroup = new DW.group({'name': self.newGroupName()});
        DW.loading();
        self.disable_add_button();
        $.post('/entity/group/create/', {
            group_name: newGroup.name(),
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        }).done(function (responseString) {
            self.enable_add_button();
            var response = $.parseJSON(responseString);
            if (response.success) {
                self.groups().push(newGroup);
                self.newGroupValid(true);
                self.show_success_message(response.message);
                self.groups.valueHasMutated();
                self.close_popup();
            }
            else {
                self.newGroupValid(false);
                self.newGroupError(response.message)
            }
        });
    };

    self.showDeleteGroupConfirmation = function(groupToDelete){
        var groupDeleteDialog = $("#group-delete-confirmation-section");
        groupDeleteDialog.find(".cancel_link").unbind('click').on('click', function(){
            groupDeleteDialog.dialog("close");
        });
        groupDeleteDialog.find("#ok_button").unbind('click').on('click', function(){
            self.deleteGroup(groupToDelete);
            groupDeleteDialog.dialog("close");
        });

        groupDeleteDialog.dialog("open");
    };

    self.close_popup = function () {
        self.newGroupName('');
        self.newGroupValid(true);
        self.newGroupError('');
        self.isOpen(false);
    };
    self.show_success_message = function (message) {
        $('#group-success').removeClass('none');
        $('#group-success').html(message);
        $('#group-success').show();
    };

    self.changeSelectedGroup = function (group) {
        $('.flash-message').remove();
        self.selectedGroup(group);
    };

    self.deleteGroup = function(group){
        group.deleteGroup().done(function(){
            self.groups.remove(group);
        });

    };

    self.selectedGroup.subscribe(function (new_group) {
        selected_group = new_group.code(); //used to send group name as filter
        $('#group-success').addClass('none');
        var table = $("#datasender_table").dataTable();
        table.fnSettings()._iDisplayStart = 0;
        table.fnReloadAjax()
    });


    self.loadGroup = function (group) {
        self.groups.push(group);
    };

    self.open = function () {
        self.isOpen(true);
    };

}
function initializeContactGroupViewModel() {
    window.groupViewModel = new ContactsGroupViewModel();
    var default_group = new DW.group({'name':gettext('All Contacts'), 'isEditable': false});
    default_group.code('');
    groupViewModel.loadGroup(default_group);
    $(existing_groups).each(function (index, group) {
        groupViewModel.loadGroup(new DW.group(group));
    });

    var groupPanel = $("#group_panel");
    ko.applyBindings(groupViewModel, groupPanel[0]);
}
