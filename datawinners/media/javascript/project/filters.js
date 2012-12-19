$.fn.datePicker = function (options) {
    return this.each(function () {
        var $this = $(this);

        var config = $.extend({}, options || {});

        $this.daterangepicker(getSettings(config.header || gettext('All Dates'), $this.data('ismonthly'))).monthpicker();
        $this.click(function () {
            var $monthpicker = $('#monthpicker_start, #monthpicker_end', $('.ranges'));
            if ($this.data('ismonthly')) {
                $monthpicker.show();
            } else {
                $monthpicker.hide();
            }
            var $visible_datepickers = $('.ui-daterangepicker:visible');
            $visible_datepickers.each(function (index, picker) {
                if ($(picker).data('for') != $this.attr('id')) {
                    $(picker).hide();
                }
            });
            $this.dropdownchecklist("close");
        });

        function getDateFormat(date_format) {
            return date_format.replace('yyyy', 'yy');
        }

        function getSettings(header, ismonthly) {
            var year_to_date_setting = {text:gettext('Year to date'), dateStart:function () {
                var x = Date.parse('today');
                x.setMonth(0);
                x.setDate(1);
                return x;
            }, dateEnd:'today' };
            var settings = {
                presetRanges:[
                    {text:header, dateStart:function () {
                        return Date.parse('1900.01.01')
                    }, dateEnd:'today', is_for_all_period:true },
                    {text:gettext('Current month'), dateStart:function () {
                        return Date.parse('today').moveToFirstDayOfMonth();
                    }, dateEnd:'today' },
                    {text:gettext('Last Month'), dateStart:function () {
                        return Date.parse('last month').moveToFirstDayOfMonth();
                    }, dateEnd:function () {
                        return Date.parse('last month').moveToLastDayOfMonth();
                    } }
                ],
                presets:{dateRange:gettext('Choose Date(s)')},
                earliestDate:'1/1/2011',
                latestDate:'21/12/2012',
                dateFormat:getDateFormat(date_format),
                rangeSplitter:'-',
                onOpen:function () {
                    $this.dropdownchecklist("close");
                }
            };
            if (ismonthly) {
                settings.presets = {dateRange:gettext('Choose Month(s)')}
            } else {
                settings.presetRanges = settings.presetRanges.concat(year_to_date_setting);
                if (typeof(ismonthly) == "undefined") {
                    settings.dateFormat = 'dd.mm.yy';
                }
            }
            return settings;
        }
    })

}