$(document).ready(function () {
    var dwAnalysis, headers,
        dataToPopulate;
    var tableElement = $("#analysis_table");

    var DwTable = (function ($, tableElement) {

        function DwTable(header, dataToPopulate) {

            //cache DOM Elements
            this.$tableName = tableElement;
            this.$tableName.append("<thead><tr></tr></thead><tbody></tbody>");
            this.$tBody = this.$tableName.find("tbody");
            this.$tHeadRow = this.$tableName.find("thead tr");
            this.dataToPopulate = dataToPopulate;
            this.header = header;

            //Default Int values
            this.headerArray = [];

            this.init();
        }

        DwTable.prototype.init = function () {
            var self = this;
            this.headerArray = [];

            this.handleHeaderArray(this.$tHeadRow, this.header, "");
            var element = self.$tBody.find("tr:last-child");
            self.handleJSONDataAsArray(self.$tBody, self.dataToPopulate, self.headerArray);
            self.populateTable();
        }

        DwTable.prototype.addHeaderToElement = function (element, value) {
            element.append('<td>' + value + '</td>');
        }

        DwTable.prototype.handleHeaderArray = function (element, array, prefix) {
            var self = this;
            $.each(array, function (index, value) {
                self.handleHeaderObject(element, value, prefix);
            });
        }

        DwTable.prototype.handleHeaderObject = function (element, jsonObject, prefix) {
            var self = this;
            var prefix;
            if (jsonObject.hasOwnProperty("id")) {
                prefix = prefix == "" ? jsonObject.id : prefix + "." + jsonObject.id;
            }
            if (jsonObject.hasOwnProperty("title")) {
                self.headerArray.push(prefix);
                self.addHeaderToElement(element, jsonObject.title);
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

        DwTable.prototype.handleJSONDataAsObject = function (element, jsonObject) {
            var self = this;
            $.each(self.headerArray, function (index, header) {
                var value = self.findProperty(jsonObject, header, "");
                self.handleJSONDataAsString(element, value);
            });
        }


        DwTable.prototype.handleJSONDataAsString = function (element, string) {
            element.append('<td>' + string + '</td>')
        }

        DwTable.prototype.handleJSONDataAsArray = function (element, array) {
            var self = this;
            $.each(array, function (index, value) {
                element.append("<tr></tr>");
                self.handleJSONDataAsObject(element.find("tr:last-child"), value);
            });
        }

        DwTable.prototype.findProperty = function (jsonObject, property, defaultValue) {
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

        DwTable.prototype.populateTable = function () {
            this.$tableName.DataTable({
                "dom": 'C<"clear">lfrtip',
                "scrollX": true,
                "ColVis": {
                    "activate": "mouseover"
                },
                columnDefs: [
                    {visible: false, targets: 2}
                ],
                colVis: {
                    restore: "Restore",
                    showAll: "Show all",
                    showNone: "Show none"
                }
            });
        }

        return DwTable;

    })($, tableElement);

     $.getJSON(headerUrl, function (response) {
        headers = response;
        $.getJSON(dataUrl, function (response) {
            dataToPopulate = response.data;
        }).done(function () {
            dwAnalysis = new DwTable(headers, dataToPopulate);
        }).fail(function (error) {
            console.log(error);
        });
    });
});

