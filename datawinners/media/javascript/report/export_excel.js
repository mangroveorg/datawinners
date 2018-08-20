var CELL_STYLE = {
    alignment: {
      vertical: "top",
      wrapText: true
    }
};

var Util = {};
Util.cellType = { "number": "n", "string":"s", "Date":"d"};

var prepareForExport = function(htmlData) {
    headers = $("#report_container th");
    headers = headers.map(function(index, element) { return $(element).text(); });
    headers = [$.makeArray(headers)];
    extractedData = [];
    var exportableFilters = getExportableFilters();

    htmlData.forEach(function(element) { var row = $(element).find('td').map(function(index, element) { return $(element).text(); }); extractedData.push($.makeArray(row)) });;
    var workbook = {
          SheetNames: ['report'], Sheets: {
            'report' : prepareExcelData(exportableFilters.concat(headers.concat(extractedData)))
          }
        };
    return exportExcel(workbook);
};


var getExportableFilters = function() {
// Safe handling when there is no filter.
    try {
        return prepareExportableFilters();
    } catch(e) {
        return [];
    }
};

var exportExcel = function(workbook) {
    return function () {
        var wbout = XLSX.write(workbook, {bookType:'xlsx', bookSST:true, type: 'binary'});
        saveAs(new Blob([s2ab(wbout)], {type:"application/octet-stream"}), "report.xlsx");
    };
};

function s2ab(s) {
    var buf = new ArrayBuffer(s.length);
    var view = new Uint8Array(buf);
    for (var i=0; i!=s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF;
    return buf;
}

function prepareExcelData(data) {
    var reportSheet = {};
    var endCol = 0;

    for(var R = 0; data.length > R; ++R) {
      for(var C = 0; data[R].length > C; ++C) {
        var cell_address = XLSX.utils.encode_cell({c:C, r:R});
        reportSheet[cell_address] = { 'v': data[R][C], 't': Util.cellType[typeof data[R][C]], 's': CELL_STYLE };
      }

      if (endCol < data[R].length) {
        endCol = data[R].length;
      }
    }

    var RANGE = {};
    RANGE.s = { r: 0, c: 0};
    RANGE.e = { r: data.length, c: endCol };

    reportSheet['!ref'] = XLSX.utils.encode_range(RANGE);
    reportSheet['!cols'] = [];
    for ( var i = 0; i < endCol; i++) {
      reportSheet['!cols'].push({ 'wch': 30});
    }

    return reportSheet;
}