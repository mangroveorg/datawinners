DW.SubmissionTabs = function () {
    var self = this;

    var tabList = ["all", "success", "error", "deleted", "analysis"];
    var active_tab_index = 0;

    self.updateActiveTabIndexBasedOnCurrentLocation = function () {
        active_tab_index = 0;
        var match = window.location.pathname.match(/tab\/([^/]+)\//);
        if (match)
            active_tab_index = tabList.indexOf(match[1]);
    };

    self.initialize_tabs = function() {
        var index_of_tab_li = active_tab_index+1;
        $('#tabs ul>li:nth-child('+index_of_tab_li+')').addClass('ui-tabs-selected ui-state-active');
    };


    self.getActiveTabIndex = function () {
        return active_tab_index;
    };

    self.setActiveTabIndex = function (tabIndex) {
        active_tab_index = tabIndex;
    };

    self.getActiveTabName = function () {
        return tabList[active_tab_index];
    };

    self.isTableEntriesCheckable = function () {
        return active_tab_index != 3;
    };

    self.setToAnalysisTab = function () {
        active_tab_index = 4;
    };
};

DW.SubmissionLogTable = function (options) {

    $.ajax({
        url: options.header_url,
        data: {"type": options.tabName, "no_cache": new Date() },
        success: function (columnDef) {
            _init_submission_log_table(columnDef)
        },
        dataType: "json"
    });

    var no_data_help = {"all": "<span>" + gettext("Once your Data Senders have sent in Submissions, they will appear here.") + "</span>" + $(".help_no_submissions").html(),
        "analysis": "<span>" + gettext("Once your Data Senders have sent in Submissions, they will appear here.") + "</span>" + $(".help_no_submissions").html(),
        "success": "<span>" + gettext("Once your Data Senders have sent in Submissions successfully, they will appear here.") + "</span>" + $(".help_no_submissions").html(),
        "error": gettext("No unsuccessful Submissions!"),
        "deleted": gettext("No deleted Submissions.")
    };

    function _init_submission_log_table(cols) {
        $(".submission_table").dwTable({
                aoColumns: cols,
                "concept": "Submission",
                "sDom": "iprtipl",
                "sAjaxSource": options.table_source_url,
                "sAjaxDataIdColIndex": 1,
                "remove_id": true,
                "bServerSide": true,
                "oLanguage": {"sEmptyTable": no_data_help[options.tabName]},
                "aaSorting": [
                    [ 2, "desc"]
                ],
                "aoColumnDefs": [
                    {"aTargets": [0], "sWidth": "30px"}
                ],
                "actionItems": options.actions_menu,
                "fnInitComplete": function () {
                    $('#search_box').append($('.dataTables_wrapper .dataTables_filter'));
                },
                "fnHeaderCallback": function (head) {
                },
                "getFilter": filter_as_json
            }
        );
        $(".submission_table").dataTable().fnSetColumnVis(0, options.row_check_box_visible)
    };
};

DW.SubmissionLogExport = function () {
    var self = this;

    self.init = function (currentTabName) {
        self.exportLink = $('.export_link');
        self.exportForm = $('#export_form');
        self.url = '/project/export/log' + '?type=' + currentTabName;
        _initialize_events();
    };

    var _initialize_events = function () {
        self.exportLink.click(function () {
            self.exportForm.appendJson({"search_filters": JSON.stringify(filter_as_json())}).attr('action', self.url).submit();
        });
    };
};

DW.DataSenderFilter = function (postFilterSelectionCallBack) {
    var self = this;
    var postFilterSelection = postFilterSelectionCallBack;
    this.datasenders_source_url = "/entity/datasenders/autocomplete/";

    self.init = function () {
        self.filter = $("#data_sender_filter");
        self.filter.data('ds_id', '');
        self.initialize_autocomplete();
        self.initialize_events();
    };

    self.initialize_autocomplete = function () {
        var self = this;
        self.filter.autocomplete({
            "source": self.datasenders_source_url,
            "select": function (event, ui) {
                self.filter.data('ds_id', ui.item.id);
                self.filter.data('label', ui.item.label);
                postFilterSelection();
            }
        }).data("autocomplete")._renderItem = function (ul, item) {
            return $("<li></li>").data("item.autocomplete", item).append($("<a>" + item.label + ' <span class="small_grey">' + item.id + '</span></a>')).appendTo(ul);
        };
    };

    self.initialize_events = function () {
        // change on autocomplete is not working in certain cases like select an item and then clear doesn't fire change event. so using input element's change.
        self.filter.change(function () {
            if (self.filter.val() == '') {
                self.filter.data('ds_id', '');
                postFilterSelection();
            }
        });

        self.filter.on("blur", function() {
            if (self.filter.data('label') != self.filter.val()) {
                self.filter.val("");
            }
        });
    };
};

DW.SubjectFilter = function (postFilterSelectionCallBack) {
    var self = this;
    var postFilterSelection = postFilterSelectionCallBack;

    self.init = function () {
        self.filter = $("#subject_filter");
        self.filter.data('value', '');
        self.initialize_autocomplete();
        self.initialize_events();
    };

    self.initialize_autocomplete = function () {
        var self = this;
        self.filter.autocomplete({
            "source": "/entity/" + entity_type + "/autocomplete/",
            "select": function (event, ui) {
                self.filter.data('value', ui.item.id);
                self.filter.data('label', ui.item.label);
                postFilterSelection();
            }
        }).data("autocomplete")._renderItem = function (ul, item) {
            return $("<li></li>").data("item.autocomplete", item).append($("<a>" + item.label + ' <span class="small_grey">' + item.id + '</span></a>')).appendTo(ul);
        };
    };

    self.initialize_events = function () {
        // change on autocomplete is not working in certain cases like select an item and then clear doesn't fire change event. so using input element's change.
        self.filter.change(function () {
            if (self.filter.val() == '') {
                self.filter.data('value', '');
                postFilterSelection();
            }
        });

        self.filter.on("blur", function() {
            if (self.filter.data('label') != self.filter.val()) {
                self.filter.val("");
            }
        });
    };
};

DW.DateFilter = function (postFilterSelectionCallBack) {
    var self = this;
    var postFilterSelection = postFilterSelectionCallBack;

    self.init = function () {
        self.filterSelects = $('.datepicker');
        _.each(self.filterSelects, function(dateTimePickerInput){
            var dateInput = $(dateTimePickerInput);
            var format = dateInput.data("format");
            var qcode = dateInput.data("question-code");
            var options = {
                             eventCallback: _closeFilterSelects,
                             onCloseCallback: _onCloseSubmissionDatePicker,
                             monthpicker:{
                                     start: {'id': "start" + qcode},
                                     end: {'id': "end" + qcode}
                             }
                          };
            if(format){
                options['date_format'] = format;
            }
            dateInput.datePicker(options);
        });
    };

    function _closeFilterSelects() {
        self.filterSelects.dropdownchecklist('close');
    };

    function _onCloseSubmissionDatePicker() {
        self.filterSelects.dropdownchecklist('close');
        postFilterSelection();
    };
};

DW.SearchTextFilter = function (postFilterSelectionCallBack) {
    var self = this;
    var postFilterSelection = postFilterSelectionCallBack;

    self.init = function () {
        self.filter = $("#search_text");
        _initialize_events();
    };

    var _initialize_events = function () {
        self.filter.keyup(function () {
            postFilterSelection();
        })
    };

};