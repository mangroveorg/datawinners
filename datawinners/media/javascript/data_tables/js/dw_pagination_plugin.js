$.fn.dataTableExt.oPagination.dw_pagination = {
    "fnInit": function (oSettings, nPaging, fnCallbackDraw) {

        $(nPaging).hide();
        nPrevious = $('<span class="paginate_button previous">&#x25C0;</span>')
        nNext = $('<span class="paginate_button next">&#x25B6;</span>')
        nMore=$('<span class="paginate_more">&#x25BE;</span>')

        var instance_id = parseInt(Math.random() * 10000000000000001);
        dropdown_id = "pagination_more_menu" + instance_id;
        first_page_id = "first_page" + instance_id;
        last_page_id = "last_page" + instance_id;
        dropdown = $('<div class="dropdown dropdown-tip" style="display:none;" id="' + dropdown_id + '">' +
                '<ul class="dropdown-menu"> <li> <a href="javascript:void(0);" id=' + first_page_id + '>' + gettext('First') +
                '</a> </li> <li> <a  id=' + last_page_id + '>' + gettext('Last') + '</a></li></div>');

        $(nPaging).append(nPrevious).append(nNext).append(nMore);
        $(document.body).append(dropdown);

        $(nMore).dropdown('attach', "#" + dropdown_id);
        $(nMore).data('first', first_page_id);
        $(nMore).data('last', last_page_id);

        $(nPrevious).click(function () {
            if ($(this).attr('class').indexOf("disabled")<0){
                oSettings.oApi._fnPageChange(oSettings, "previous");
                fnCallbackDraw(oSettings);
            }
        });

        $(nNext).click(function () {
            if ($(this).attr('class').indexOf("disabled")<0){
                oSettings.oApi._fnPageChange(oSettings, "next");
                fnCallbackDraw(oSettings);
            }
        });

        $("#"+first_page_id).click(function(){
             if (!$(this).parent().hasClass("disabled")){
                oSettings.oApi._fnPageChange(oSettings, "first");
                fnCallbackDraw(oSettings);
                 return true;
             }
            return false;
        });

        $("#"+last_page_id).click(function(){
             if (!$(this).parent().hasClass("disabled")){
                oSettings.oApi._fnPageChange(oSettings, "last");
                fnCallbackDraw(oSettings);
                return true;
             }
            return false;
        });

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

            if (oSettings._iDisplayStart === 0 && oSettings.fnDisplayEnd() == oSettings.fnRecordsDisplay()) {
                buttons[2].className = "paginate_more_disabled dropdown-disabled";
            } else {
                buttons[2].className = "paginate_more";
            }

            var first_id = $(an[i]).find(".paginate_more").data('first');
            var last_id = $(an[i]).find(".paginate_more").data('last');
            if (oSettings._iDisplayStart === 0) {
                buttons[0].className = "paginate_disabled_previous";
                $($("#" + first_id).parent()).addClass('disabled');
            }
            else {
                buttons[0].className = "paginate_enabled_previous";
                $($("#" + first_id).parent()).removeClass('disabled')
            }

            if (oSettings.fnDisplayEnd() == oSettings.fnRecordsDisplay()) {
                buttons[1].className = "paginate_disabled_next";
                $($("#" + last_id).parent()).addClass('disabled')
            }
            else {
                buttons[1].className = "paginate_enabled_next";
                $($("#" + last_id).parent()).removeClass('disabled')
            }

        }
    }
};