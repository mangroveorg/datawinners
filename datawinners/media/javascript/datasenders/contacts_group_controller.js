DW.group = function (group) {
    var defaults = {
        name: '',
        code:''
    };
    this.options = $.extend(true, defaults, group);
    this._init();
};
DW.group.prototype = {
    _init: function () {
        var g = this.options;
        this.name = ko.observable(g.name);
        this.code = ko.observable(g.name);
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
    self.addGroupDialogContent = ko.observable($('#add_group_dialog_content').html());

    self.addNewGroup = function () {
        var newGroup = new DW.group({'name': self.newGroupName()});
        self.groupButtonText(gettext("Adding..."));
        $.post('/entity/group/create/', {
            group_name: newGroup.name(),
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        })
            .done(function (responseString) {
                self.groupButtonText(gettext('Add'));
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
    self.close_popup = function () {
        self.newGroupName('');
        self.newGroupValid(true);
        self.newGroupError('');
        self.isOpen(false);
    };
    self.show_success_message = function (message) {
        $('#group-success').removeClass('none');
        $('#group-success').html(message);
    };

    self.changeSelectedGroup = function (group) {
        self.selectedGroup(group);
    };

    self.selectedGroup.subscribe(function (new_group) {
        selected_group = new_group.code(); //used to send group name as filter
        $("#datasender_table").dataTable().fnReloadAjax()
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
    var default_group = new DW.group({'name':'All Contacts'});
    default_group.code('');
    groupViewModel.loadGroup(default_group);
    $(existing_groups).each(function (index, group) {
        groupViewModel.loadGroup(new DW.group(group));
    });
}
