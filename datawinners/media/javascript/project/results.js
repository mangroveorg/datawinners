$(document).ready(function () {
    var datasender_filter_id ;
    function load_table(tab_name) {
        var url = render_table_url + "/headers";
        $.ajax({
            url: url,
            data: {"type": tab_name, "no_cache": new Date() },
            success: function (columnDef) {
                init_submission_log_table(columnDef)
            },
            dataType: "json"
        });
    }

    function activate_tab(tab_name) {

        $('#search_box .dataTables_filter').remove();
        $('.submission_table').dataTable().fnDestroy();
        $('.submission_table').empty();
        DW.loading();
        load_table(tab_name);
    }

    var $actionBar = $(".action_bar");
    var $dataTable = $('.submission_table');
    var tab = ["all", "success", "error", "deleted"];
    var no_data_help = {"all": "<span>" + gettext("Once your Data Senders have sent in Submissions, they will appear here.") + "</span>" + $(".help_no_submissions").html(),
        "success": "<span>" + gettext("Once your Data Senders have sent in Submissions successfully, they will appear here.") + "</span>" + $(".help_no_submissions").html(),
        "error": gettext("No unsuccessful Submissions!"),
        "deleted": gettext("No deleted Submissions.")
    }
    var active_tab_index = 0;
    var match = window.location.pathname.match(/tab\/([^/]+)\//);
    if (match) active_tab_index = tab.indexOf(match[1]);


    $.ajaxSetup({ cache: false });
    load_table(tab[active_tab_index]);

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

        if (active_tab_index === tab_index) {
            return;
        }
        active_tab_index = tab_index;
        //window.location.href = window.location.pathname + '?type=' + tab[active_tab_index];
        activate_tab(tab[active_tab_index]);
        return true;
    });
    var all_tabs = $("#tabs").tabs().find('>ul>li>a[href$=tab_template]');
    for (var i = 0; i < all_tabs.length; i++) {
        if (i == active_tab_index) {
            $($(all_tabs[i]).parent()).addClass('ui-tabs-selected ui-state-active')
        } else {
            $($(all_tabs[i]).parent()).removeClass('ui-tabs-selected ui-state-active')
        }

    }
    $(".ui-corner-all").removeClass("ui-corner-all");
    $(".ui-corner-top").removeClass("ui-corner-top");


    $('.export_link').click(function () {
        var url = '/project/export/log' + '?type=' + tab[active_tab_index];
        $('#export_form').appendJson(DW.get_criteria()).attr('action', url).submit();
    });
    function init_submission_log_table(cols) {

        var action_handler = new DW.SubmissionLogActionHandler(tab[active_tab_index], project_id);
        var url = render_table_url + '?type=' + tab[active_tab_index];
        var display_check_box = active_tab_index != 3;
        var actions = display_check_box ? [
            {"label": "Edit", handler: action_handler['edit'], "allow_selection": "single"},
            {"label": "Delete", handler: action_handler['delete'], "allow_selection": "multiple"}
        ] : []
        $(".submission_table").dwTable({
                aoColumns: cols,
                "concept": "Submission",
                "sDom": "iprtipl",
                "sAjaxSource": url,
                "sAjaxDataIdColIndex": 1,
                "remove_id": true,
                "bServerSide": true,
                "oLanguage": {"sEmptyTable": no_data_help[tab[active_tab_index]]},
                "aaSorting": [
                    [ 2, "desc"]
                ],
                "aoColumnDefs": [
                    {"aTargets": [0], "sWidth": "30px"}
                ],
                "actionItems": actions,
                "fnInitComplete": function () {
                    $('#search_box').append($('.dataTables_wrapper .dataTables_filter'));
                },
                "fnHeaderCallback": function (head) {
                }

                , "getFilter": function () {
                    return {"submissionDatePicker": $('#submissionDatePicker').val(),
                            "datasenderFilter": $("#data_sender_filter").data('ds_id'),
                            "reportingPeriodPicker": $('#reportingPeriodPicker').val(),
                            "search_text":$('#search_text').val() };
                }
            }

        );
        $(".submission_table").dataTable().fnSetColumnVis(0, display_check_box)

    }


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
});



