$(document).ready(function () {

    var analysisTable,
        colCustomization;

    var tableElement = $("#analysis_table");
    var AnalysisPageDataTable = (function ($, tableElement) {
        function AnalysisPageDataTable(columns) {
            tableElement.DataTable({
                "dom": '<ip<t>ipfl>',
                "language": {
                    "info": interpolate(gettext("<b>%(start)s to %(end)s</b> of %(total)s %(subject_type)s(s)"),
                        {
                            'start': '_START_',
                            'end': '_END_',
                            'total': '_TOTAL_',
                            subject_type: gettext("Submission")
                        }, true),
                    "lengthMenu": gettext("Show") + ' _MENU_ ' + gettext("Submission")
                },
                "scrollX": true,
                "searching": false,
                "processing": true,
                "serverSide": true,
                "ajax": {
                    url: dataUrl
                },
                "columns": columns,
                "initComplete": function (settings, json) {
                    $('.dataTables_scrollBody thead tr').css({visibility: 'collapse'});
                    $(".paging_dw_pagination").show();
                },
                "pagingType": "dw_pagination",
                "columnDefs": [{
                    "targets": "media",
                    "data": null,
                    "defaultContent": "<button>Click!</button>"
                }]
            });
        };

        return AnalysisPageDataTable;
    })($, tableElement);

    $.getJSON(headerUrl, function (columns) {
        analysisTable = new AnalysisPageDataTable(columns);
    });


    /*Col Customization Widget*/

    var ColCustomWidget = (function($){
        function ColCustomWidget(customizationHeader) {
            this.$dataTable = $(".analysis_tbl_wrapper");
            this.$columnWidget = $(".customization-widget");
            this.$custMenu = $(".customization-menu");
            this.$colWidgetActions = $("#cust-icon, .customization-widget-close");
            this.$customizationIcon = $("#cust-icon");
            this.$selectAll = $(".select-all");
            this.$selectNone = $(".select-none");
            this.$customizationOverlay = $(".customization-overlay");
            this.$pageHeader = $("#container_header_application");
            this.$pageContent = $("#container_content");

            this.items = customizationHeader;
            this.init();

            //Bind initial click events
            this.bindEvents();
        }

        ColCustomWidget.prototype.init = function () {
            //Start constructing the widget with loaded Items
            this.constructItems(this.items);
        };

        ColCustomWidget.prototype.bindEvents = function () {

            var self = this;
            var customizationOverlayHeight;

            this.$colWidgetActions.on("click", function () {
                if (self.$dataTable.hasClass("shrink")) {
                    self.$dataTable.removeClass("shrink");
                    self.$columnWidget.removeClass("expand");
                    self.$customizationOverlay.hide();
                    self.$customizationIcon.removeClass("active");
                    self.submit();
                  } else {
                    self.$columnWidget.addClass("expand");
                    self.$dataTable.addClass("shrink");
                    customizationOverlayHeight = self.$pageHeader.outerHeight() + self.$pageContent.outerHeight() + 30;
                    self.$customizationOverlay.height(customizationOverlayHeight).show();
                    self.$customizationIcon.addClass("active");
                }
            });

            this.$customizationOverlay.on("click", function () {
                self.$dataTable.removeClass("shrink");
                self.$columnWidget.removeClass("expand");
                $(this).hide();
                self.submit();
            });


            $(".customization-menu span").on("click", function (event) {
                var $checkBox = $(this).prev("input[type=checkbox]");
                $checkBox.prop("checked", !$checkBox.prop("checked"));
                event.stopPropagation();
            });

            this.$selectAll.on("click", function () {
                self.$custMenu.find("input[type=checkbox]").prop('checked', true);
            });

            this.$selectNone.on("click", function () {
                self.$custMenu.find("input[type=checkbox]").prop('checked', false);
            });

            $(".customization-menu input[type=checkbox]").click(function (event) {
                if (this.checked) {
                    $(this).parents('li').children('input[type=checkbox]').prop('checked', true);
                }
                $(this).parent().find('input[type=checkbox]').prop('checked', this.checked);
                event.stopPropagation();
            });

        };

        ColCustomWidget.prototype.constructItems = function (customizationHeader) {
            var self = this;
            $.each(customizationHeader, function (index, value) {
                var $newParentElement = self.createColItems("ul", value, self.$custMenu);

                if (value.hasOwnProperty('children') && (value.children.length > 0)) {
                    self.iterateItems(value.children, $newParentElement);
                }
            });
        };

        ColCustomWidget.prototype.createColItems = function(element, value, parentElement) {
            var $listElement = $('<'+ element + '/>'),
                $checkBox = $("<input type='checkbox' value='True' name='" + value.data + "'>");

            $checkBox.prop('checked', value.visibility);
            $listElement.append("<span title='" + value.title +"'>" + value.title + "</span>").prepend($checkBox);
            parentElement.append($listElement);

            return $listElement;
        };

        ColCustomWidget.prototype.iterateItems = function (items, $parentElement) {
            var self = this;
            $.each(items, function (index, value) {
                if (value.hasOwnProperty('children') && (value.children.length > 0)) {
                    var $newParentElement = self.createColItems("ul", value, $parentElement);
                    self.constructChildNodes(value, $newParentElement);
                } else {
                    self.constructChildNodes(value, $parentElement);
                }
            });
        };

        ColCustomWidget.prototype.constructChildNodes = function (value, $parentElement) {
            if (value.hasOwnProperty('children') && (value.children.length > 0)) {
                this.iterateItems(value.children, $parentElement);
            } else {
                this.createColItems("li", value, $parentElement);
            }
        };
        
        ColCustomWidget.prototype.submit = function(){
        	$.ajax({
        		  type: "POST",
        		  url: preferenceUrl,
        		  data: $("#customization-form").serialize(),
        		  success: self.submitSuccess,
        		  dataType: 'json'
        		});
    	};
    	
        ColCustomWidget.prototype.submitSuccess = function(){
        	//reload the table
        	//TODO
        };

        return ColCustomWidget;
    })($);

    $.getJSON(preferenceUrl, function (customizationHeader) {
        colCustomization = new ColCustomWidget(customizationHeader);
    });

    /*Chart View*/
    var $dataTableViews = $(".chart-view-icon, .list-view-icon"),
        $chartViewIcon = $(".chart-view-icon"),
        $listViewIcon = $(".list-view-icon"),
        $chartViewWrapper = $("#chart_ol"),
        $chartViewInfo = $("#chart_info"),
        $customizationMenu = $("#cust-icon");

    $dataTableViews.on("click", function (event) {
        if($(event.target).hasClass("active") || $(event.target).closest("li").hasClass("active")) {
            return;
        }
        if ($("#analysis_table_wrapper").css("display") == "none") {
            $chartViewIcon.removeClass("active");
            $listViewIcon.addClass("active");
            $chartViewWrapper.hide();
            $chartViewInfo.hide();
            $customizationMenu.show();
            $("#analysis_table_wrapper").show();
        } else {
            $chartViewIcon.addClass("active");
            $listViewIcon.removeClass("active");
            $("#analysis_table_wrapper").hide();
            $chartViewWrapper.show();
            $chartViewInfo.show();
            $customizationMenu.hide();
        }
    });

    $('[data-toggle="tooltip"]').tooltip();
});
