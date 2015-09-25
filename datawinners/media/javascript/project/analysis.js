$(document).ready(function () {
    var tableElement = $("#analysis_table");
    var AnalysisPageDataTable = (function($,tableElement){
    	function AnalysisPageDataTable(columns){
            tableElement.DataTable({
                "scrollX": true,
                "scrollY": "374px",
                "searching": false,
                "processing": true,
                "serverSide": true,
                "ajax": {
                    url: dataUrl
                },
                "columns":   columns
            });    		
    	};
    	
    	return AnalysisPageDataTable;
    })($, tableElement);
    
    $.getJSON(headerUrl, function (columns) {
        analysisTable = new AnalysisPageDataTable(columns);
    });
    
});

