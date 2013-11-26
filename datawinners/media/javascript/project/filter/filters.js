$.fn.datePicker = function (options) {
    return this.each(function () {
        var $this = $(this);
        var config = $.extend({}, options || {});
        $this.daterangepicker(getSettings(config, config.header || gettext('All Dates'), $this.data('ismonthly'))).monthpicker();
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
        });

        function getDateFormat(date_format) {
            return date_format.replace('yyyy', 'yy');
        }

        function getSettings(config, header, ismonthly) {
            var year_to_date_setting = {text: gettext('Year to date'), dateStart: function () {
                var x = Date.parse('today');
                x.setMonth(0);
                x.setDate(1);
                return x;
            }, dateEnd: 'today' };
            var settings = {
                presetRanges: [
                    {text: header, dateStart: function () {
                        return Date.parse('1900.01.01')
                    }, dateEnd: 'today', is_for_all_period: true },
                    {text: gettext('Current month'), dateStart: function () {
                        return Date.parse('today').moveToFirstDayOfMonth();
                    }, dateEnd: 'today' },
                    {text: gettext('Last Month'), dateStart: function () {
                        return Date.parse('last month').moveToFirstDayOfMonth();
                    }, dateEnd: function () {
                        return Date.parse('last month').moveToLastDayOfMonth();
                    } }
                ],
                presets: {dateRange: gettext('Choose Date(s)')},
                earliestDate: '1/1/2011',
                latestDate: '21/12/2012',
                dateFormat: getDateFormat(date_format),
                rangeSplitter: '-'
            };
            if (ismonthly) {
                settings.presets = {dateRange: gettext('Choose Month(s)')}
            } else {
                settings.presetRanges = settings.presetRanges.concat(year_to_date_setting);
                if (typeof(ismonthly) == "undefined") {
                    settings.dateFormat = 'dd.mm.yy';
                }
            }
            settings.eventCallback = config.eventCallback
            return settings;
        }
    })
}

DW.get_criteria = function () {
//    var reporting_period = DW.get_datepicker_value($('#reportingPeriodPicker'), gettext("All Periods"));
//    var submission_date = DW.get_datepicker_value($('#submissionDatePicker'), gettext("All Dates"));
//    var subject_ids = $('#subjectSelect').attr('ids');
//    var submission_sources = $('#dataSenderSelect').attr('data');
    var search = $('.dataTables_filter input').val();
    $(".dateErrorDiv").hide();
    return {
//        'start_time': $.trim(reporting_period.start_time),
//        'end_time': $.trim(reporting_period.end_time),
//        'submission_date_start': $.trim(submission_date.start_time),
//        'submission_date_end': $.trim(submission_date.end_time),
//        'subject_ids': subject_ids,
//        'submission_sources': submission_sources,
        'search': search
    };
}

    var $filterSelects = $('#submissionDatePicker');

    function buildRangePicker() {
        $('#submissionDatePicker').datePicker({eventCallback: closeFilterSelects});
    }

DW.get_datepicker_value = function ($datePicker, default_text) {
    var data = $datePicker.val().split("-");
    if (data[0] == "" || data[0] == default_text) {
        data = ['', ''];
    } else if (data[0] != default_text && Date.parse(data[0]) == null) {
        $datePicker.next().html('<label class=error>' + gettext("Enter a correct date. No filtering applied") + '</label>').show();
        data = ['', ''];
    } else if (data.length == 1) {
        data[1] = data[0];
    }
    return {start_time: data[0], end_time: data[1]};
}

DW.disable_filter_section_if_no_data = function () {
    if ($('#dataSenderSelect>option').size() != 0) {
        return false;
    }
    var $filters = $(".ui-dropdownchecklist, .ui-dropdownchecklist-selector, .ui-dropdownchecklist-text, #keyword, #reportingPeriodPicker, #submissionDatePicker").add($('#go').removeClass('button_blue').addClass('button_disabled'));
    $filters.attr('disabled', 'disabled').addClass('disabled').filter('span').find('>span').addClass('disabled').end().unbind('click');

    $('.filter_label').addClass('grey')
};


    function closeFilterSelects() {
        $filterSelects.dropdownchecklist('close')
    }