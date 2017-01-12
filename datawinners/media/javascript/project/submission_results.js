    DW.SubmissionTabs = function () {
    var self = this;

    var tabList = ["all", "success", "error", "duplicates", "deleted", "analysis"];
    var active_tab_index = 0;

    self.updateActiveTabIndexBasedOnCurrentLocation = function () {
        active_tab_index = 0;
        var match = window.location.pathname.match(/tab\/([^/]+)\//);
        if (match)
            active_tab_index = tabList.indexOf(match[1]);
    };

    self.initialize_tabs = function() {
        var index_of_tab_li = active_tab_index+1;
        $('#tabs').find('ul>li:nth-child('+index_of_tab_li+')').first().addClass('ui-tabs-selected ui-state-active');
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
        return active_tab_index != 4;
    };

    self.isDuplicatesTab = function () {
        return active_tab_index == 3;
    };

    self.setToAnalysisTab = function () {
        active_tab_index = 5;
    };
};

DW.SubmissionLogTable = function (options) {

    $.ajax({
        url: options.header_url,
        data: {"type": options.tabName, "no_cache": new Date() },
        success: function (columnDef) {
            _init_submission_log_table(columnDef);

        },
        dataType: "json"
    });

    var no_data_help = {"all": "<span id=\"help_text_chart\">" + gettext("Once your Data Senders have sent in Submissions, they will appear here.") + "</span>" ,
        "analysis": "<span>" + gettext("Once your Data Senders have sent in Submissions, they will appear here.") + "</span>",
        "success": "<span>" + gettext("Once your Data Senders have sent in Submissions successfully, they will appear here.") + "</span>",
        "error": gettext("No unsuccessful Submissions!"),
        "deleted": gettext("No deleted Submissions."),
        "duplicates": gettext("No Duplicates are currently available for the given time period based on your choice.") + "</span>"
    };

    var paginateGroups = {"duplicates": true}
    var concept = {"duplicates":"Duplicate"}

    function _init_submission_log_table(cols) {
        $(".submission_table").dwTable({
                aoColumns: cols,
                "concept": concept[options.tabName]? concept[options.tabName]: "Submission",
                "sDom": "iprtipl",
                "sAjaxSource": options.table_source_url,
                "sAjaxDataIdColIndex": 1,
                "remove_id": true,
                "bServerSide": true,
                "paginateGroups": paginateGroups[options.tabName]? true: false,
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
                    if(options.tabName != 'analysis'){
                        $('.analysis_help_text').remove();
                    }
                },
                "fnHeaderCallback": function (head) {
                },
                "fnRowCallback": function(row, data, dataIndex) {
                    if (dataIndex == 0) {
                        return row;
                    }

                    table = $(".submission_table").dataTable();
                    prevRow = $(table.fnGetNodes(dataIndex-1));
                    prevRowData = table.fnGetData(dataIndex-1);
                    if (
                        (prevRow.hasClass("odd_group") && (data[data.length-1] == prevRowData[data.length-1])) ||
                        (!prevRow.hasClass("odd_group") && (data[data.length-1] != prevRowData[data.length-1]))
                       ) {
                      $(row).addClass("odd_group");
                    }
                    return row;
                },
                "getFilter": filter_as_json
            }
        );
        $(".submission_table").dataTable().fnSetColumnVis(0, options.row_check_box_visible);
    }
};

DW.SubmissionLogExport = function () {
    var self = this;

    self.init = function () {
        self.exportLink = $('.export_link');
        self.exportSingleSheetLink = $('.export_single_sheet_link');
        self.exportForm = $('#export_form');
        _initialize_dialogs();
        _initialize_events();
    };

    self.update_tab = function(currentTabName){
        self.url = '/project/export/log' + '?type=' + currentTabName;
        self.count_url = '/project/export/log-count' + '?type=' + currentTabName;
    };

    self._show_export_message = function(){
        var messageBox = $("#export-warning");
        messageBox.removeClass("none");
        $("#close-export-msg").on('click', function(){
            messageBox.addClass("none");
        });
    };

    var _updateAndSubmitForm = function(is_export_with_media, is_single_sheet){
        if (is_export_with_media)
        {
            self._show_export_message();
        }
        self.exportForm.appendJson(
            {
                "search_filters": JSON.stringify(filter_as_json()),
                "is_media": is_export_with_media,
                "is_single_sheet": is_single_sheet
            }
        ).attr('action', self.url).submit();
    };

    var _check_limit_and_export = function(is_export_with_media, is_single_sheet){
        $.post(self.count_url, {
                'data': JSON.stringify({"questionnaire_code": $("#questionnaire_code").val(),
                                        "search_filters": filter_as_json()
                                        }),
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            }
        ).done(function(data){
                if(data['count'] <= 20000){
                   _updateAndSubmitForm(is_export_with_media, is_single_sheet);
                }
                else{
                    DW.trackEvent('export-submissions', 'export-exceeded-limit', user_email + ":" + organization_name);
                    self.limit_dialog.show();
                }
        });
    };

    var _initialize_dialogs = function(){

       var limit_info_dialog_options = {
                successCallBack: function (callback) {
                },
                title: gettext("Number of Submissions Exceeds Export Limit"),
                link_selector: ".export_link",
                dialogDiv: "#export_submission_limit_dialog",
                cancelLinkSelector: "#cancel_dialog",
                width: 580
            };
       self.limit_dialog = new DW.Dialog(limit_info_dialog_options).init();
    };

    var _initialize_events = function () {
        $('.with_media').click(function(){
               DW.trackEvent('export-submissions-with-images', 'export-submissions-single-sheet', user_email + ":" + organization_name);
               _check_limit_and_export(true, false);
         });

        self.exportLink.click(function () {
               DW.trackEvent('export-submissions', 'export-submissions-single-sheet', user_email + ":" + organization_name);
               _check_limit_and_export(false, false);
        });

        self.exportSingleSheetLink.click(function () {
               DW.trackEvent('export-submissions', 'export-submissions-single-sheet', user_email + ":" + organization_name, 'single sheet');
               _check_limit_and_export(false, true);
        });

    };
};

DW.DuplicatesForFilter = function(postFilterSelectionCallBack) {
    var self = this;

    self.init = function() {
        $("#duplicates_for").change(postFilterSelectionCallBack);
        $("#duplicates_for").on('change', function(){
            DW.trackEvent('submissions', 'searched-by-duplicates-for', $("#duplicates_for option:selected").val());
        });
    };
}

DW.DuplicatesHelpSection = function(){

    function _closeDialogHandler(){
        $("#duplicates_learn_more_text").dialog('close');
    }

    function _initializeDialog(dialogSection){
        dialogSection.dialog({
                autoOpen: false,
                width: 940,
                modal: true,
                position:"top",
                title: gettext("Learn More About Duplicates"),
                zIndex: 1100,
                open: function(){
                    $(".learn_more_accordion").accordion({collapsible: true,active: false});
                },
                close: function(){
                    $(".learn_more_accordion").accordion( "destroy" );
                }
        });
        dialogSection.off('click', '#close_duplicates_learn_more_section', _closeDialogHandler);
        dialogSection.on('click', '#close_duplicates_learn_more_section', _closeDialogHandler);
    }

    this.init = function(){
        $("#duplicates_learn_more_link").on('click', function(){
            var dialogSection = $("#duplicates_learn_more_text");
            _initializeDialog(dialogSection);
            dialogSection.removeClass("none");
            dialogSection.dialog("open");
            dialogSection.parent(".ui-dialog")[0].scrollIntoView();
        });
    }
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
                DW.trackEvent('submissions', 'searched-by-datasender');
                postFilterSelection();
            }
        }).data("autocomplete")._renderItem = function (ul, item) {
            return $("<li></li>").data("item.autocomplete", item).append($("<a>" + item.label + ' <span class="small_grey">' + item.id + '</span></a>')).appendTo(ul);
        };
    };

    self.initialize_events = function () {
        // change on autocomplete is not working in certain cases like select an item and then clear doesn't fire change event. so using input element's change.
        self.filter.change(function() {
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
        self.filters.each(function(i,el){$(el).data('value', '');});
        self.initialize_autocomplete();
        self.initialize_events();
    };

    self.initialize_autocomplete = function () {
        var self = this;
        self.filters.each(function(i, el){
        var $el = $(el);
        var unique_id_type = $el.attr('entity_type');
        $el.autocomplete({
            "source": "/entity/" + unique_id_type + "/autocomplete/",
            "select": function (event, ui) {
                $el.data('value', ui.item.id);
                $el.data('label', ui.item.label);
                DW.trackEvent('submissions', 'searched-by-unique-id', unique_id_type);
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
        });

        self.filters.each(function(i,el){
            $(el).on("blur", function() {
                if($(el).data('label') != $(el).val()){
                    $(el).val("");
                }
            });

        });
    };
};

DW.DateFilter = function (postFilterSelectionCallBack) {
    var self = this;

    self.init = function () {
        var callbackWrapper = function(){
           DW.trackEvent('submissions', 'searched-by-date');
           postFilterSelectionCallBack();
        };

        self.filterSelects = $('.datepicker');
        _.each(self.filterSelects, function(dateTimePickerInput){
            var dateInput = $(dateTimePickerInput);
            var format = dateInput.data("format");
            var qcode = dateInput.data("question-code");
            var options = {
                             onCloseCallback: callbackWrapper,
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
        self.filter.keyup(function() {
            DW.trackEvent('submissions', 'free-text-search-submissions');
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
    }

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