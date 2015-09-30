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



    /*Col Customization Widget*/

    var customizationHeader = [
        {

            "data": "f6fefb725df211e5bd150800275f9736_q3",
            "title": "level 0",
            "visibility":true,
            "children":[
                {
                  "title":"level 1",
                  "data":"datasender.mobile_number",
                  "visibility":false,
                  "children":[]
                },
                {
                    "title":"level 1a",
                    "data":"datasender.email",
                    "visibility":true,
                    "children":[
                        {
                          "title":"level 2",
                          "data":"datasender.mobile_number",
                          "visibility":true,
                          "children":[]
                        },
                        {
                            "title":"level 2a",
                            "data":"datasender.email",
                            "visibility":true
                        }
                    ]
                }
            ]
        },
        {
            "data": "f6fefb725df211e5bd150800275f9736_q4",
            "title": "level 0a",
            "visibility":true
        }
    ];


    var ColCustomWidget = (function($){
        function ColCustomWidget(customizationHeader) {
            this.$dataTable = $(".analysis_tbl_wrapper");
            this.$columnWidget = $(".customization_widget");
            this.$custIcon = $(".cust_icon");

            this.items = customizationHeader;
            this.init();
        }

        ColCustomWidget.prototype.init = function() {
            var self = this;

            //Start constructing the widget with loaded Items
            this.constructItems(this.items);

            this.$custIcon.on("click", function(){
                  if(self.$dataTable.hasClass("shrink")) {
                    self.$dataTable.removeClass("shrink");
                    self.$columnWidget.removeClass("expand");
                  } else {
                    self.$dataTable.addClass("shrink");
                    self.$columnWidget.addClass("expand");
                  }
            });

            $(".customization_widget input[type=checkbox]").click(function(){
                if(this.checked){
                    $(this).parents('li').children('input[type=checkbox]').prop('checked',true);
                }
                $(this).parent().find('input[type=checkbox]').prop('checked',this.checked);
            });
        };

        ColCustomWidget.prototype.constructItems = function(customizationHeader) {
            var self = this;
            $.each(customizationHeader, function(index, value) {
                var $newParentElement = self.createColItems("ul", value, self.$columnWidget);

                if(value.hasOwnProperty('children') && (value.children.length > 0)) {
                   self.iterateItems(value.children, $newParentElement);
                }
            });
        };

        ColCustomWidget.prototype.createColItems = function(element, value, parentElement) {
            var $listElement = $('<'+ element + '/>'),
                $checkBox = $("<input type='checkbox' value='" + value.title + "'>");

            $checkBox.prop('checked', value.visibility);
            $listElement.text(value.title).prepend($checkBox);
            parentElement.append($listElement);

            return $listElement;
        };

        ColCustomWidget.prototype.iterateItems = function(items, $parentElement) {
            var self = this;
            $.each(items, function(index, value){
                if(value.hasOwnProperty('children') && (value.children.length > 0)) {
                    var $newParentElement = self.createColItems("ul", value, $parentElement);
                    self.constructChildNodes(value, $newParentElement);
                } else {
                    self.constructChildNodes(value, $parentElement);
                }
            });
        };

        ColCustomWidget.prototype.constructChildNodes = function(value, $parentElement) {
            if (value.hasOwnProperty('children') && (value.children.length > 0)) {
                this.iterateItems(value.children, $parentElement);
            } else {
                this.createColItems("li", value, $parentElement);
            }
        };

        return ColCustomWidget;
    })($);

    colCustomization = new ColCustomWidget(customizationHeader);

});
