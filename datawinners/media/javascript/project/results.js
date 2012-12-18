$(document).ready(function () {
    $(document).ajaxStop($.unblockUI);
    var $no_submission_hint = $('.help_no_submissions');
    var $page_hint = $('#page_hint');
    var tab = ["all", "success", "error", "deleted"];
    var active_tab_index;
    $("#tabs").tabs().find('>ul>li>a').click(function(){
        var tab_index = $(this).parent().index();
        if (active_tab_index != tab_index) {
            fetch_data(tab_index);
            active_tab_index = tab_index;
        }
    }).filter(':first').trigger('click');

    function fetch_data(active_tab_index) {
        DW.loading();
        $.ajax({
            type:'POST',
            url:window.location.pathname + '?type=' + tab[active_tab_index],
            data:{},
            success:function (response) {
                var response_data = JSON.parse(response);
                show_data(active_tab_index, response_data.data_list);
            }});
    }

    var dataBinding = function (data, destroy, retrive, emptyTableText) {
        $('.submission_table').dataTable({
            "bDestroy":destroy,
            "bRetrieve":retrive,
            "sPaginationType":"full_numbers",
            "aaData":data,
            "bSort":false,
            "oLanguage":{
                "sProcessing":gettext("Processing..."),
                "sLengthMenu":gettext("Show _MENU_ Submissions"),
                "sZeroRecords":emptyTableText,
                "sEmptyTable":emptyTableText,
                "sLoadingRecords":gettext("Loading..."),
                "sInfo":gettext("<span class='bold'>_START_ - _END_</span> of <span id='total_count'>_TOTAL_</span> Submissions"),
                "sInfoEmpty":gettext("0 Submissions"),
                "sInfoFiltered":gettext("(filtered from _MAX_ total Data records)"),
                "sInfoPostFix":"",
                "sSearch":gettext("Search:"),
                "sUrl":"",
                "oPaginate":{
                    "sFirst":gettext("First"),
                    "sPrevious":gettext("Previous"),
                    "sNext":gettext("Next"),
                    "sLast":gettext("Last")
                },
                "fnInfoCallback":null
            },
            "sDom":'<"@dataTables_info"i>rtpl<"@dataTable_search">',
            "iDisplayLength":25
        });
    };

    function show_data(active_tab_index, data) {
        var index = (active_tab_index || 0) + 1;
        $page_hint.find('>div:nth-child(' + index + ')').show().siblings().hide();
        var emptyTableText = $no_submission_hint.filter(':eq(' + active_tab_index + ')').clone(true).html();
        dataBinding(data, true, false, emptyTableText);
        wrap_table();
    }

    var wrap_table = function () {
        $(".submission_table").wrap("<div class='data_table' style='width:" + ($(window).width() - 65) + "px'/>");
    };
});

