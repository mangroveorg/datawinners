$(document).ready(function () {

    var analysisTable,
        colCustomization;

    var tableElement = $("#analysis_table");
    var $analysisLoader = $(".analysis-ajax-loader");

    var AnalysisPageDataTable = (function ($, tableElement) {
        function AnalysisPageDataTable(columns) {
            tableElement.DataTable({
                "pageLength": 25,
                "dom": '<ip<t>ipfl>',
                "language": {
                    "info": interpolate(gettext("<b>%(start)s to %(end)s</b> of %(total)s %(subject_type)s(s)"),
                        {
                            'start': '_START_',
                            'end': '_END_',
                            'total': '_TOTAL_',
                            subject_type: gettext("Submission")
                        }, true),
                    "lengthMenu": gettext("Show") + ' _MENU_ ' + gettext("Submission"),
                    "emptyTable": gettext("No data available in table")
                },
                "scrollX": true,
                "searching": false,
                "processing": true,
                "serverSide": true,
                "ajax": {
                    url: dataUrl,
                    type: "POST",
                    data: function(d) {
                		d.data_sender_filter = $("#data_sender_filter").data('ds_id');
                		d.search_text = $('#search_text').val();
                		d.submission_date_range = $('#submissionDatePicker').val();
                        var subject_filter = {};
                        $('input.subject_filter').each(function(index, element){
                            var entity_type = element.getAttribute('search-key');
                            var data = $(element).data('value');
                            if(data != '')
                                subject_filter[entity_type] = data;
                        });
                        d.uniqueIdFilters = JSON.stringify(subject_filter);
                        var date_filters = {};
                        $('input.date-question-filter').each(function(index, element){
                            var question_code = $(element).data('questionCode');
                            var searchKey = element.getAttribute('search-key');
                            var format = $(element).data('questionCode');
                            var question_code = element.getAttribute('data-question-code');
                            date_filters[question_code] = {
                                'dateRange': element.value,
                                'searchKey': searchKey,
                                'format': $(element).data('format')
                            };
                        });
                        d.dateQuestionFilters = JSON.stringify(date_filters);
                    },
                    beforeSend: function() {
                        $analysisLoader.show();
                    },
                    complete: function() {
                        $analysisLoader.hide();
                    }
                },
                "order":[0,"desc"], //submission date
                "columns": columns,
                "initComplete": function (settings, json) {
                    $('.dataTables_scrollBody thead tr').css({visibility: 'collapse'});
                    $(".paging_dw_pagination").show();
                },
                "drawCallback": function (settings, json) {
                    $('.dataTables_scrollBody thead tr').css({visibility: 'collapse'});
                },
                "pagingType": "dw_pagination",
                "columnDefs": [{
                    "targets": "media",
                    "data": null,
                    "defaultContent": "<button>Click!</button>"
                }],
                "rowCallback": function (row, data, rowIndex) {
                    var columnsInDataTable = this.dataTableSettings[0].aoColumns;
                    var visibleColumns = $.grep(columnsInDataTable, function (e) {
                            return e.bVisible != false;
                        });
                    $.each(data.media, function (key, value) {
                        var result = $.grep(columnsInDataTable, function (e) {
                            return e.sName == key;
                        });
                        var columnIndex = -1;
                        for(var i =0; i< visibleColumns.length; i++) {
                            if (key == visibleColumns[i].name) {
                                columnIndex = i;
                                break;
                            }
                        }
                        if(columnIndex == -1) {
                            return row;
                        }
                        var html = '';
                        switch (value.type) {
                            case 'image':
                                html = '<img src="' + value.preview_link + '">';
                                html = html + '<br>';
                                html = html + '<a href="' + value.download_link + '">' + value.value + '</a>';
                                break;

                            case 'audio':
                                html = "<audio controls>" +
                                    "<source src='" + value.download_link + "' type='audio/ogg'> \
                                            Your browser does not support the audio tag. \
                                        </audio><br><a href='"+ value.download_link + "'>Download</a>";
                                break;

                            case 'video':
                                html = "<video controls>" +
                                    "<source src='" + value.download_link + "' type='video/mp4'> \
                                            Your browser does not support the audio tag. \
                                        </video><br><a href='"+ value.download_link + "'>Download</a>";
                                break;
                        }
                        $(row).find("td").eq(columnIndex).html(html);
                    });
                    return row;
                }
            });

            this.handleEmptyTable();
        };

        AnalysisPageDataTable.prototype.handleEmptyTable = function () {
            $('.dataTables_scrollBody thead tr').css({visibility: 'collapse'});
            var isAnyColumnVisible = tableElement.DataTable().columns().visible().reduce(function (a, b) {
                return a || b
            });
            if (!isAnyColumnVisible) {
                $('#analysis_table_empty').show();
                $('.paging_dw_pagination,.dataTables_info,.dataTables_length,.dataTables_scroll').css('visibility', 'hidden');
            } else {
                $('#analysis_table_empty').hide();
                $('.paging_dw_pagination,.dataTables_info,.dataTables_length,.dataTables_scroll').css('visibility', 'visible');
            }
        }
        return AnalysisPageDataTable;
    })($, tableElement);

    $.getJSON(headerUrl, function (columns) {
        analysisTable = new AnalysisPageDataTable(columns);
    });


    /*Column Customization Widget*/

    var ColCustomWidget = (function ($) {
        function ColCustomWidget(customizationHeader) {
            this.$columnWidget = $(".customization-widget");
            this.$custMenu = $(".customization-menu");
            this.$colWidgetActions = $("#customize-btn, .customization-widget-close, .customize-list-link");
            this.$customizationIcon = $("#customize-btn");
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

            this.$colWidgetActions.on("click", function (event) {
                console.log("clicked customization");
                if (self.$customizationIcon.hasClass("active")) {
                    self.$columnWidget.hide();
                    self.$customizationOverlay.hide();
                    self.$customizationIcon.removeClass("active");
                    self.submit();
                } else {
                    self.$columnWidget.show();
                    customizationOverlayHeight = self.$pageHeader.outerHeight() + self.$pageContent.outerHeight() + 30;
                    if(customizationOverlayHeight > 970) {
                        customizationOverlayHeight = customizationOverlayHeight + 5;
                    } else {
                        customizationOverlayHeight = 970;
                    }
                    self.$customizationOverlay.height(customizationOverlayHeight).show();
                    self.$customizationIcon.addClass("active");
                }
                event.stopPropagation();
            });

            this.$customizationOverlay.on("click", function () {
                self.$columnWidget.hide();
                self.$customizationIcon.removeClass("active");
                $(this).hide();
                self.submit();
            });


            /*Column Customisation click events*/
            this.$selectAll.on("click", function () {
                self.$custMenu.find("input[type=checkbox]").prop('checked', true);
                self.handleVisibility();
                tableElement.DataTable().draw('page');
            });

            this.$selectNone.on("click", function () {
                self.$custMenu.find("input[type=checkbox]").prop('checked', false);
                self.handleVisibility();
                tableElement.DataTable().draw('page');
            });

            $(".customization-menu input[type=checkbox]").click(function (event) {
                self.handleCheckBoxes(this);
                event.stopPropagation();
                tableElement.DataTable().draw('page');
            });

            $(".customization-menu span").on("click", function (event) {
                var $checkBox = $(this).prev("input[type=checkbox]");

                $checkBox[0].checked = !$checkBox[0].checked;
                self.handleCheckBoxes($checkBox[0]);
                event.stopPropagation();
                tableElement.DataTable().draw('page');
            });

            /*Tooltip for long questionnaires on column customisation widget*/
            $('[data-toggle="tooltip"]').tooltip();
        };

        ColCustomWidget.prototype.handleCheckBoxes = function(element) {
            var self = this;

            if($(element).parent("ul").length == 0) {

                var $parentElement =$(element).closest("ul"),
                    $listElements = $parentElement.children("li"),
                    $inputElementsLength = $listElements.find("input[type=checkbox]").length;

                if($listElements.find("input:checkbox:checked").length != $inputElementsLength) {
                    $parentElement.find("> input:checkbox").prop('checked', false);
                } else {
                    $parentElement.find("> input:checkbox").prop('checked', true);
                }

            }

            $(element).parent().find('input[type=checkbox]').prop('checked', element.checked);
            self.handleVisibility(element);
        };

        ColCustomWidget.prototype.handleVisibility = function (element) {
            var self = this;

            //Recursively handle all column visibility
            if (!element) {
                self.$custMenu.find("input[type=checkbox]").each(function (index, element) {
                    self.handleVisibility(element);
                });
                return;
            }

            $(element).parent().find('li > input[type=checkbox]').each(function (index, elem) {
                self.handleVisibility(elem);
            });
            self.updateTable(element.name, element.checked);
            analysisTable.handleEmptyTable();
        };

        ColCustomWidget.prototype.updateTable = function (columnName, visibility) {
            var column = tableElement.DataTable().column(columnName + ':name');
            column.visible(visibility);
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

        ColCustomWidget.prototype.createColItems = function (element, value, parentElement) {
            var toolTipText = value.title.replace(/'/g, "&#39;"),
                $listElement = $('<' + element + '/>'),
                $checkBox = $("<input type='checkbox' value='True' name='" + value.data + "'>");

            $checkBox.prop('checked', value.visibility);
            $listElement.append("<span title='" + toolTipText + "'>" + value.title + "</span>").prepend($checkBox);
            parentElement.append($listElement);

            return $listElement;
        };

        ColCustomWidget.prototype.sortItems = function(items){
            firstCols = [];
            otherCols = []
            $.each(items, function (index, value) {
                if (value.data.indexOf('.q2') >= 0 || value.data.indexOf('.q6') >= 0) {
                    firstCols.push(value)
                }
                else {
                    otherCols.push(value)
                }
            });
            var concat = firstCols.concat(otherCols);
            return concat;
        };

        ColCustomWidget.prototype.iterateItems = function (items, $parentElement) {
            var sortedItems = this.sortItems(items);
            var self = this;
            $.each(sortedItems, function (index, value) {
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

        ColCustomWidget.prototype.submit = function () {
            $.ajax({
                type: "POST",
                url: preferenceUrl,
                data: $("#customization-form").serialize(),
                success: self.submitSuccess,
                dataType: 'json'
            });
        };

        ColCustomWidget.prototype.submitSuccess = function () {
            //reload the table
            //TODO
        };

        return ColCustomWidget;
    })($);

    $.getJSON(preferenceUrl, function (customizationHeader) {
        colCustomization = new ColCustomWidget(customizationHeader);
    });


    DW.SubmissionAnalysisView = function(){

        var self = this;
        var tableViewOption = $("#table_view_option");
        var chartViewOption = $("#chart_view_option");
        var tableView = $("#submission_logs");
        var chartView = $('#chart_ol');
        var customizationView = $('#customize-btn');
        var isChartViewShown = false;
        var submissionTabs = new DW.SubmissionTabs();
        var chartGenerator = new DW.SubmissionAnalysisChartGenerator();

        self.init = function() {
           _initializeEvents();
           _initializeExport();
        };

        var _initializeExport = function () {
            var submissionLogExport = new DW.SubmissionLogExport();
            submissionTabs.setToAnalysisTab();
            submissionLogExport.update_tab(submissionTabs.getActiveTabName());
            submissionLogExport.init();
        };

        var _initializeEvents = function(){
            tableViewOption.on("click", _showDataTableView);
            chartViewOption.on("click", _showChartView);
        };

        var _showDataTableView = function () {
            if (!isChartViewShown)
                return;
            tableViewOption.addClass("active");
            chartViewOption.removeClass("active-right");
            customizationView.show();
            _reinitializeSubmissionTableView();
            chartView.hide();
            isChartViewShown = false;
            tableElement.DataTable().draw();
        };

        var _postFilterSelection = function() {
    	    if(isChartViewShown)
                chartGenerator.generateCharts();
            else
                tableElement.DataTable().draw();
        };

        var _initialize_filters = function(){
            new DW.DateFilter(_postFilterSelection).init();
            new DW.DataSenderFilter(_postFilterSelection).init();
            new DW.SubjectFilter(_postFilterSelection).init();
            new DW.SearchTextFilter(_postFilterSelection).init();
        };

        _initialize_filters();

        var _reinitializeSubmissionTableView = function() {
            tableView.show();
            $('.submission_table').dataTable().fnDestroy();
            $('.submission_table').empty();
            $('#chart_info').empty();
            $('#chart_info_2').empty();
            chartView.empty();
        };

        var _showChartView = function () {
            if (isChartViewShown)
                return;
            DW.trackEvent('chart-view', 'chart-view-link-clicked');
            tableViewOption.removeClass("active");
            chartViewOption.addClass("active-right");
            customizationView.hide();
            isChartViewShown = true;
            tableView.hide();
            chartGenerator.generateCharts();
        };

    };

    DW.SubmissionAnalysisChartGenerator = function(){
        var self = this;
        var chartView = $('#chart_ol');

        self.generateCharts = function() {
             $.ajax({
                    "dataType": 'json',
                    "type": "POST",
                    "url": analysis_stats_url,
                    "data": {
                		data_sender_filter: $("#data_sender_filter").data('ds_id'),
                		search_text: $('#search_text').val(),
                		submission_date_range: $('#submissionDatePicker').val()
                    },
                    "success": function (response) {
                           chartView.show();
                          _draw_bar_charts(response);
                    },
                    "error": function () {
                    },
                    "global": false
             });
        };

        var _draw_bar_charts = function(response) {
            var $chart_ol = chartView.attr('style', 'width:' + ($(window).width() - 85) + 'px').empty();

            if (response.total == 0) {
                $('#chart_info').empty().append("<b>" + response.total + "</b> " + gettext("Submissions"))
                var html = "<span id='no_charts_here'>" + gettext("Once your Data Senders have sent in Submissions, they will appear here.") + "</span>";
                showNoSubmissionExplanation(chartView, html);
                return;
            } else if ($.isEmptyObject(response.result)){
                showNoSubmissionExplanation(chartView, gettext("You do not have any multiple choice questions (Answer Type: List of choices) to display here."));
                return;
            }

            var i = 0;
            $.each(response.result, function (index, ans) {
                drawChartBlockForQuestions(index, ans, i, $chart_ol);
                drawChart(ans, i, response.total, "");
                i++;
            });
        };
    };

    new DW.SubmissionAnalysisView().init();
    new DW.FilterSection().init();
});


