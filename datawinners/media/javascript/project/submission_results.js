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
        $('#tabs ul>li:nth-child('+index_of_tab_li+')').first().addClass('ui-tabs-selected ui-state-active');
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
                    [ options.sortCol, "desc"]
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
        _initialize_dialog();
        _initialize_events();
    };

    var _updateAndSubmitForm = function(){
        self.exportForm.appendJson({"search_filters": JSON.stringify(filter_as_json())}).attr('action', self.url).submit();
    };

    var _initialize_dialog = function(){
       var dialogOptions = {
                successCallBack: function (callback) {
                    DW.trackEvent('export-submissions', 'export-submissions-multiple-sheet');
                    callback();
                    _updateAndSubmitForm();
                },
                title: gettext("Submission Exceeds Number of Supported Columns."),
                link_selector: ".export_link",
                dialogDiv: "#export_submission_multiple_sheet_dialog",
                cancelLinkSelector: "#cancel_dialog",
                width: 580
            };
       self.dialog = new DW.Dialog(dialogOptions).init();
    };

    var _initialize_events = function () {
        self.exportLink.click(function () {
           if(is_submission_exported_to_multiple_sheets === 'True'){
                self.dialog.show();
           }
           else{
               DW.trackEvent('export-submissions', 'export-submissions-single-sheet');
               _updateAndSubmitForm();
           }
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
        self.filters = $(".subject_filter");
        self.filters.each(function(i,el){$(el).data('value', '');})
        self.initialize_autocomplete();
        self.initialize_events();
    };

    self.initialize_autocomplete = function () {
        var self = this;
        self.filters.each(function(i, el){
        var $el = $(el);
        $el.autocomplete({
            "source": "/entity/" + $el.attr('entity_type') + "/autocomplete/",
            "select": function (event, ui) {
                $el.data('value', ui.item.id);
                $el.data('label', ui.item.label);
                postFilterSelection();
            }
        }).data("autocomplete")._renderItem = function (ul, item) {
            return $("<li></li>").data("item.autocomplete", item).append($("<a>" + item.label + ' <span class="small_grey">' + item.id + '</span></a>')).appendTo(ul);
        };
            });
    };

    self.initialize_events = function () {
        // change on autocomplete is not working in certain cases like select an item and then clear doesn't fire change event. so using input element's change.
        self.filters.each(function(i, el){
            $(el).change(function () {
            if ($(el).val() == '') {
                $(el).data('value', '');
                postFilterSelection();
            }
        });
        })

        self.filters.each(function(i,el){
            $(el).on("blur", function() {
            if ($(el).data('label') != $(el).val()) {
                $(el).val("");
            }
        });

        });
    };
};

DW.DateFilter = function (postFilterSelectionCallBack) {
    var self = this;

    self.init = function () {
        self.filterSelects = $('.datepicker');
        _.each(self.filterSelects, function(dateTimePickerInput){
            var dateInput = $(dateTimePickerInput);
            var format = dateInput.data("format");
            var qcode = dateInput.data("question-code");
            var options = {
                             onCloseCallback: postFilterSelectionCallBack,
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

DW.FilterSection = function(){
    var self = this;
    var showFilter;
    var hideFilter;
    var parentSection;
    var filterSection;

    function _destroyTooltip(element) {
        $(element).removeData('tooltip').unbind();
    }

    function _initializeTooltipForLongQuestionLabels() {
        $.each($("#questionnaire_field_filters").find('.help_icon'), function (index, element) {
            if (element.offsetWidth < element.scrollWidth) {
                DW.ToolTip({target: $(element)});
            }
        });
    }

    function _removeAllTooltips(){
        $.each($("#questionnaire_field_filters").find('.help_icon'), function (index, element) {
           _destroyTooltip(element);
        });
    };

    self.init = function(){
        showFilter = $("#show_filters");
        hideFilter = $("#hide_filters");
        filterSection = $("#questionnaire_field_filters");
        parentSection = $("#filter_section");
        _initializeEventHandlers();
        _removeAllTooltips();
        _initializeTooltipForLongQuestionLabels();
        filterSection.addClass('none');
    };

    function _initializeEventHandlers(){

        showFilter.on("click", function () {
            $(this).addClass('none');
            filterSection.removeClass('none');
            parentSection.removeClass("filter_section_padded");
        });

        hideFilter.on("click", function () {
            filterSection.addClass('none');
            showFilter.removeClass('none');
            parentSection.addClass("filter_section_padded");
        });
    }
};