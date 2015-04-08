DW.group = function (group) {
    var self = this;

    var defaults = {
        name: '',
        code:'',
        isEditable: true
    };
    this.options = $.extend(true, defaults, group);

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
        this.code = ko.observable(g.name);
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
        var newGroupName = $('#new_group_name').val().trim();

        if(newGroupName){
            $("#new_group_mandatory_error").addClass("none");
        }
        else{
            $("#new_group_mandatory_error").find(".validationText").text(gettext('This field is required.'));
            $("#new_group_mandatory_error").removeClass("none");
            return;
        }
        if (newGroupName == group.name()){
            self.show_success_message(gettext("Your changes have been saved."));
            $("#group-rename-confirmation-section").dialog('close');
        }
        else {
            DW.loading();
            self.disable_rename_button()
            $.post(group_rename_url, {
                group_name: group.name(),
                new_group_name: newGroupName,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            }).done(function (response){
                var response = $.parseJSON(response);
                if(response.success){
                    group.updateName(newGroupName);
                    self.changeSelectedGroup(group);
                    self.show_success_message(gettext("Your changes have been saved."));
                    $("#group-rename-confirmation-section").dialog('close');
                }
                else{
                    $("#new_group_mandatory_error").find(".validationText").text(response.message);
                    $("#new_group_mandatory_error").removeClass("none");
                }
                self.enable_rename_button();
            }).error(function(){
                alert("Rename threw an exception");
            });
        }
    };
    self.disable_rename_button = function() {
            var rename_button = $("#group-rename-confirmation-section").find("#ok_button");
            rename_button.text(gettext('Renaming...'));
            rename_button.addClass('ui-state-disabled');
    };
    self.enable_rename_button = function(){
            var rename_button = $("#group-rename-confirmation-section").find("#ok_button");
            rename_button.text(gettext('Rename'));
            rename_button.removeClass('ui-state-disabled');
    };


    self.addNewGroup = function () {
        var newGroup = new DW.group({'name': self.newGroupName().trim()});
        DW.loading();
        self.disable_add_button();
        $.post('/entity/group/create/', {
            group_name: newGroup.name(),
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        }).done(function (responseString) {
            self.enable_add_button();
            var response = $.parseJSON(responseString);
            if (response.success) {
                self.groups.push(newGroup);
                self.newGroupValid(true);
                self.show_success_message(response.message);
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
            self.setSelectedGroupToDefault();

        });

        groupDeleteDialog.dialog("open");
    };

    self.showRenameGroupConfirmation = function(groupToRename){
        var groupRenameDialog = $("#group-rename-confirmation-section");
        groupRenameDialog.find(".cancel_link").unbind('click').on('click', function(){
                groupRenameDialog.dialog("close");
            });

        groupRenameDialog.find("#ok_button").unbind('click').on('click', function() {
            self.confirmGroupRename(groupToRename);
        });
        $('#new_group_name').val(groupToRename.name());

        groupRenameDialog.dialog("open");

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

    self.setSelectedGroupToDefault = function(){
        self.selectedGroup(self.groups()[0]);
    };

    self.deleteGroup = function(group){
        DW.loading();
        $.post(delete_group_url, {
            'group_name': group.name(),
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        }).done(function(){
            self.groups.remove(group);
            self.show_success_message(gettext("Group(s) successfully deleted."));
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
