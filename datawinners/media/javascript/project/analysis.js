var dwAnalysis, totalEntries;
$(document).ready(function () {
    var headers,
        dataToPopulate;
    var tableElement = $("#analysis_table");

    var DynamicHeaderDataTable = (function ($, tableElement) {

        function DynamicHeaderDataTable(header, dataToPopulate, totalEntries) {

            //cache DOM Elements
            this.$tableName = tableElement;

            //this.$pagination = $(".dataTables_paginate");

            this.dataToPopulate = dataToPopulate;
            this.header = header;

            //Default Int values
            this.headerArray = [];
            this.currentPageIndex = 0;
            this.sortColumn = header[0].id;
            this.sortAscending = true;
            this.totalEntries = totalEntries;
            this.size = $('select[name=analysis_table_length]').val() || 25;
            this.totalPages = Math.ceil(this.totalEntries/this.size);
            this.init();
        }

        DynamicHeaderDataTable.prototype.init = function () {
            var self = this;
            this.$tableName.append("<thead><tr></tr></thead><tbody></tbody>");
            this.$tBody = this.$tableName.find("tbody");
            this.$tHeadRow = this.$tableName.find("thead tr");
            this.handleHeaderArray(this.$tHeadRow, this.header, "");
            var element = self.$tBody.find("tr:last-child");
            self.handleJSONDataAsArray(self.$tBody, self.dataToPopulate, self.headerArray);
            self.populateTable();

            $(".dataTables_paginate").on("click", function (event) {
                var e = $(event.target);
                var pageIndex = self.currentPageIndex;
                var requestedPageIndex = e.attr("data-dt-idx");
                if (e.hasClass("disabled") || self.currentPageIndex == requestedPageIndex)
                    return;
                if (e.hasClass("next")) {
                    pageIndex++;
                } else if (e.hasClass("previous")) {
                    pageIndex--;
                } else {
                    pageIndex = requestedPageIndex;
                }
                self.fetchData(pageIndex)
            });

            this.$tHeadRow.on("click", function (event) {
                var e = $(event.target);
                var currentColumn = event.target.getAttribute('data-columncode');
                if (currentColumn == self.sortColumn)
                    self.sortAscending = !self.sortAscending;
                else
                    self.sortAscending = true;
                self.fetchData(self.currentPageIndex);
            });

        }

        DynamicHeaderDataTable.prototype.addHeaderToElement = function (element, value) {
            element.append('<th data-columncode=' + value.id + '>' + value.title + '</th>');
        }

        DynamicHeaderDataTable.prototype.handleHeaderArray = function (element, array, prefix) {
            var self = this;
            $.each(array, function (index, value) {
                self.handleHeaderObject(element, value, prefix);
            });
        }

        DynamicHeaderDataTable.prototype.handleHeaderObject = function (element, jsonObject, prefix) {
            var self = this;
            var prefix;
            if (jsonObject.hasOwnProperty("id")) {
                prefix = prefix == "" ? jsonObject.id : prefix + "." + jsonObject.id;
            }
            if (jsonObject.hasOwnProperty("title")) {
                self.headerArray.push(prefix);
                self.addHeaderToElement(element, jsonObject);
                return;
            }
            $.each(jsonObject, function (key, value) {
                if (value instanceof Array) {
                    self.handleHeaderArray(element, value, prefix);
                } else if (typeof(value) == "string") {
                    return;
                } else {
                    self.handleHeaderObject(element, value, prefix);
                }
            });
        }

        DynamicHeaderDataTable.prototype.handleJSONDataAsObject = function (element, jsonObject) {
            var self = this;
            $.each(self.headerArray, function (index, header) {
                var value = self.findProperty(jsonObject, header, "");
                self.handleJSONDataAsString(element, value);
            });
        }


        DynamicHeaderDataTable.prototype.handleJSONDataAsString = function (element, string) {
            element.append('<td>' + string + '</td>')
        }

        DynamicHeaderDataTable.prototype.handleJSONDataAsArray = function (element, array) {
            var self = this;
            $.each(array, function (index, value) {
                element.append("<tr></tr>");
                self.handleJSONDataAsObject(element.find("tr:last-child"), value);
            });
        }

        DynamicHeaderDataTable.prototype.findProperty = function (jsonObject, property, defaultValue) {
            if (typeof defaultValue == 'undefined')
                defaultValue = null;
            property = property.split('.');
            for (var i = 0; i < property.length; i++) {
                if (typeof jsonObject[property[i]] == 'undefined')
                    return defaultValue;
                jsonObject = jsonObject[property[i]];
            }
            return jsonObject;
        }

        DynamicHeaderDataTable.prototype.fetchData = function (pageIndex) {
            var self = this;
            var from = pageIndex * self.size;
            self.currentPageIndex = pageIndex;
            sortColumn = self.sortColumn || "";
            isSortAscending = self.sortAscending || true;
            var order = isSortAscending ? "asc" : "desc";
            var params = $.param({
                "from": from,
                "size": size,
                "sort": sortColumn,
                "order": order
            });

            $.getJSON(dataUrl + "?" + params, function (response) {
                $.blockUI({
                    message: '<h1><img src="/media/images/ajax-loader.gif"/><span class="loading">' + gettext("Just a moment") + '...</span></h1>',
                    css: {width: '275px'}
                });
                self.dataToPopulate = response.data;
            }).done(function () {

                table = self.$tableName.dataTable();
                oSettings = table.fnSettings();

                table.fnClearTable(this);

                self.handleJSONDataAsArray(self.$tBody, self.dataToPopulate, self.headerArray);


                oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
                table.fnDraw();
                //self.handleJSONDataAsArray(self.dataToPopulate)
                //self.handleJSONDataAsArray(self.$tableName, self.dataToPopulate);
                //self.populateTable();
            });
        };

        DynamicHeaderDataTable.prototype.populateTable = function () {
            var self = this;
            this.$tableName.DataTable({
                "dom": 'C<"clear">lfrtip',
                "scrollX": true,
                "scrollY": "450px",
                "searching": false
            });
        }

        return DynamicHeaderDataTable;

    })($, tableElement);

    $.getJSON(headerUrl, function (response) {
        headers = response;
        $.getJSON(dataUrl, function (response) {
            totalEntries = response.total || 0;
            dataToPopulate = response.data;
        }).done(function () {
            dwAnalysis = new DynamicHeaderDataTable(headers, dataToPopulate, totalEntries);
        }).fail(function (error) {
            console.log(error);
        });
    });
});

