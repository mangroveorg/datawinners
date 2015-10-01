$(document).ready(function () {



    var tableElement = $("#analysis_table");
    var AnalysisPageDataTable = (function($,tableElement){
    	function AnalysisPageDataTable(columns){
            tableElement.DataTable({
                "dom": '<ip<t>ipfl>',
                "language":{
                    "info": interpolate(gettext("<b>%(start)s to %(end)s</b> of %(total)s %(subject_type)s(s)"),
                    {'start': '_START_', 'end': '_END_', 'total': '_TOTAL_', subject_type: gettext("Submission")}, true),
                    "lengthMenu": gettext("Show") + ' _MENU_ ' + gettext("Submission")
                },
                "scrollX": true,
                "searching": false,
                "processing": true,
                "serverSide": true,
                "ajax": {
                    url: dataUrl
                },
                "columns":   columns,
                "initComplete": function(settings, json) {
                    $(".paging_dw_pagination").show();
                },
                "pagingType": "dw_pagination"
            });
    	};

    	return AnalysisPageDataTable;
    })($, tableElement);
    
    $.getJSON(headerUrl, function (columns) {
        analysisTable = new AnalysisPageDataTable(columns);
    });

});
