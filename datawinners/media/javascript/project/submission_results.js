$(document).ready(function () {

    var submissionTabs = new DW.SubmissionTabs();
    submissionTabs.updateActiveTabIndexBasedOnCurrentLocation();

    var _getTableActionsMenu = function(submissionTabs){
      var action_handler = new DW.SubmissionLogActionHandler(submissionTabs.getActiveTabName(), project_id);
      var table_actions_menu = submissionTabs.isTableEntriesCheckable() ? [
            {"label": "Edit", handler: action_handler['edit'], "allow_selection": "single"},
            {"label": "Delete", handler: action_handler['delete'], "allow_selection": "multiple"}
        ] : [];
      return table_actions_menu;
    };

    var _initTable = function(submissionTabs){
        var submission_table_options = {
            header_url: render_table_url + "/headers",
            table_source_url: render_table_url + '?type=' + submissionTabs.getActiveTabName(),
            row_check_box_visible: submissionTabs.isTableEntriesCheckable(),
            actions_menu: _getTableActionsMenu(submissionTabs),
            tabName: submissionTabs.getActiveTabName()
        };
        new DW.SubmissionLogTable(submission_table_options);
    };

    function activate_tab(submissionTabs) {

        $('#search_box .dataTables_filter').remove();
        $('.submission_table').dataTable().fnDestroy();
        $('.submission_table').empty();
        DW.loading();
        _initTable(submissionTabs);
    };

//    var $actionBar = $(".action_bar");
    var $dataTable = $('.submission_table');


    $.ajaxSetup({ cache: false });

    _initTable(submissionTabs);
    var $no_submission_hint = $('.help_no_submissions')
    var $page_hint = $('#page_hint');
    var $page_hint_section = $('#page_hint_section')
    $page_hint_section.text($page_hint.find('>div:first').text())
    var message = gettext("No submissions available for this search. Try changing some of the filters.");
    var help_all_data_are_filtered = "<div class=\"help_accordion\" style=\"text-align: left;\">" + message + "</div>";

    $("#tabs").tabs().find('>ul>li>a[href$=tab_template]').click(function () {
        if ($dataTable.parents('.dataTables_wrapper').length >= 1) {
            DW.current_sort_order = $dataTable.dataTable().fnSettings().aaSorting;
        } else {
            DW.current_sort_order = [
                [2, "desc"]
            ];
        }
        var tab_index = $(this).parent().index();

        if (submissionTabs.getActiveTabIndex() === tab_index) {
            return;
        }
        submissionTabs.setActiveTabIndex(tab_index);
        activate_tab(submissionTabs);
        return true;
    });

    var all_tabs = $("#tabs").tabs().find('>ul>li>a[href$=tab_template]');
    for (var i = 0; i < all_tabs.length; i++) {
        if (i == submissionTabs.getActiveTabIndex()) {
            $($(all_tabs[i]).parent()).addClass('ui-tabs-selected ui-state-active')
        } else {
            $($(all_tabs[i]).parent()).removeClass('ui-tabs-selected ui-state-active')
        }

    }

    $(".ui-corner-all").removeClass("ui-corner-all");
    $(".ui-corner-top").removeClass("ui-corner-top");


    $('.export_link').click(function () {
        var url = '/project/export/log' + '?type=' + submissionTabs.getActiveTabName();
        $('#export_form').appendJson({"search_filters":JSON.stringify(filter_as_json())}).attr('action', url).submit();
    });


    buildRangePicker();
    $("#data_sender_filter").data('ds_id','');
    $("#data_sender_filter").autocomplete({
            "source":"/entity/datasenders/autocomplete/",
            "select":function(event,ui){
                $("#data_sender_filter").data('ds_id',ui.item.id);
                $(".submission_table").dataTable().fnDraw();
            }
        }).data( "autocomplete" )._renderItem = function( ul, item ) {
        return $("<li></li>").data("item.autocomplete", item).append($("<a>" + item.label + ' <span class="small_grey">' + item.id + '</span></a>')).appendTo(ul);
    };

    // change on autocomplete is not working in certain cases like select an item and then clear doesn't fire change event. so using input element's change.
    $('#data_sender_filter').change(function(){
        if ($('#data_sender_filter').val() == ''){
                 $("#data_sender_filter").data('ds_id','');
                 $(".submission_table").dataTable().fnDraw();
         }
    });
    $("#search_text").keyup(function(){
       $(".submission_table").dataTable().fnDraw();
    })

    var entity_type = $("#subject_filter").attr('entity_type')
    $("#subject_filter").data('value','');
    $("#subject_filter").autocomplete({
            "source":"/entity/" + entity_type + "/autocomplete/"    ,
            "select":function(event,ui){
                $("#subject_filter").data('value',ui.item.id);
                $(".submission_table").dataTable().fnDraw();
            }
        }).data( "autocomplete" )._renderItem = function( ul, item ) {
        return $("<li></li>").data("item.autocomplete", item).append($("<a>" + item.label + ' <span class="small_grey">' + item.id + '</span></a>')).appendTo(ul);
    };
    $('#subject_filter').change(function(){
        if ($('#subject_filter').val() == ''){
                 $("#subject_filter").data('value','');
                 $(".submission_table").dataTable().fnDraw();
         }
    });

});

DW.SubmissionLogTable = function(options){

    $.ajax({
        url: options.header_url,
        data: {"type": options.tabName, "no_cache": new Date() },
        success: function (columnDef) {
            _init_submission_log_table(columnDef)
        },
        dataType: "json"
    });

    var no_data_help = {"all": "<span>" + gettext("Once your Data Senders have sent in Submissions, they will appear here.") + "</span>" + $(".help_no_submissions").html(),
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

DW.SubmissionTabs = function(){
        var self = this;

        var tabList = ["all", "success", "error", "deleted"];
        var active_tab_index = 0;

        self.updateActiveTabIndexBasedOnCurrentLocation = function(){
            active_tab_index = 0;
            var match = window.location.pathname.match(/tab\/([^/]+)\//);
            if (match)
                active_tab_index = tabList.indexOf(match[1]);
        };

        self.getActiveTabIndex = function(){
            return active_tab_index;
        }

        self.setActiveTabIndex = function(tabIndex){
            active_tab_index = tabIndex;
        };

        self.getActiveTabName = function(){
            return tabList[active_tab_index];
        };

        self.isTableEntriesCheckable = function(){
           return active_tab_index != 3;
        };

};





