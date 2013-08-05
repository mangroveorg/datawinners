$.fn.dataTableExt.oPagination.dw_pagination = {
    "fnInit": function (oSettings, nPaging, fnCallbackDraw) {
        nPrevious = document.createElement('span');
        nNext = document.createElement('span');
        nMore = document.createElement('span');

        nPrevious.appendChild(document.createTextNode(oSettings.oLanguage.oPaginate.sPrevious));
        nNext.appendChild(document.createTextNode(oSettings.oLanguage.oPaginate.sNext));
        nMore.appendChild(document.createTextNode("▾"));

        nPrevious.className = "paginate_button previous";
        nNext.className = "paginate_button next";
        nMore.className = "paginate_more"

        nPaging.appendChild(nPrevious);
        nPaging.appendChild(nNext);
        nPaging.appendChild(nMore);

//        $(nFirst).click(function () {
//            oSettings.oApi._fnPageChange(oSettings, "first");
//            fnCallbackDraw(oSettings);
//        });

        $(nPrevious).click(function () {
            oSettings.oApi._fnPageChange(oSettings, "previous");
            fnCallbackDraw(oSettings);
        });

        $(nNext).click(function () {
            oSettings.oApi._fnPageChange(oSettings, "next");
            fnCallbackDraw(oSettings);
        });

//        $(nLast).click(function () {
//            oSettings.oApi._fnPageChange(oSettings, "last");
//            fnCallbackDraw(oSettings);
//        });

        /* Disallow text selection */
        $(nPrevious).bind('selectstart', function () {
            return false;
        });
        $(nNext).bind('selectstart', function () {
            return false;
        });
    },


    "fnUpdate": function (oSettings, fnCallbackDraw) {
        if (!oSettings.aanFeatures.p) {
            return;
        }

        /* Loop over each instance of the pager */
        var an = oSettings.aanFeatures.p;
        for (var i = 0, iLen = an.length; i < iLen; i++) {
            var buttons = an[i].getElementsByTagName('span');
            if (oSettings._iDisplayStart === 0) {
                buttons[0].className = "paginate_disabled_previous";
            }
            else {
                buttons[0].className = "paginate_enabled_previous";
            }

            if (oSettings.fnDisplayEnd() == oSettings.fnRecordsDisplay()) {
                buttons[1].className = "paginate_disabled_next";
            }
            else {
                buttons[1].className = "paginate_enabled_next";
            }

            if (oSettings._iDisplayStart === 0 && oSettings.fnDisplayEnd() == oSettings.fnRecordsDisplay()){
                buttons[2].className = "paginate_more_disabled";
            } else {
                buttons[2].className = "paginate_more";
            }
        }
    }
};