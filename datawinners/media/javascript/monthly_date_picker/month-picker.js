/**
 * MIT License
 * Copyright (c) 2011, Luciano Costa
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

/**
 * GPL LIcense
 * Copyright (c) 2011, Luciano Costa
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program. If not, see <http://www.gnu.org/licenses/>.
 */

(function ($) {

    var methods = {
        init:function (options) {
            return this.each(function () {
                var
                    $this = $(this),
                    data = $this.data('monthpicker'),
                    year = (new Date()).getFullYear(),
                    month = (new Date()).getMonth() + 1,
                    settings = $.extend({
                        pattern:'mm.yyyy',
                        startYear:year - 10,
                        finalYear:year + 10,
                        monthNames:[gettext('Jan'), gettext('Feb'), gettext('Mar'), gettext('Apr'), gettext('May'), gettext('Jun'), gettext('Jul'), gettext('Aug'), gettext('Sep'), gettext('Oct'), gettext('Nov'), gettext('Dec')]
                    }, options),
                    settings_start = $.extend({
                            year:year,
                            month:month,
                            month_name:'',
                            id:"monthpicker_start"
                        }
                        , options.start),
                    settings_end = $.extend({
                            year:year,
                            month:month,
                            month_name:'',
                            id:"monthpicker_end"
                        }
                        , options.end);

                settings.dateSeparator = settings.pattern.replace(/(mmm|mm|m|yyyy|yy|y)/ig, '');

                // If the plugin hasn't been initialized yet for this element
                if (!data) {
                    $(this).data('monthpicker', {
                        'target':$this,
                        'settings':settings,
                        'settings_start':settings_start,
                        'settings_end':settings_end
                    });

                    $this.monthpicker('mountWidget', settings, settings_start);
                    $this.monthpicker('mountWidget', settings, settings_end);
                    $this.monthpicker('mountMP');

                    $this.bind('monthpicker-click-month', function (e, element) {
                        selectedChanged(element);
                        $this.monthpicker('setValue', settings, settings_start, settings_end);
                    });

                    $this.bind('monthpicker-change-year', function (e) {
                        $this.monthpicker('setValue', settings, settings_start, settings_end);
                    });

                    $(document).mousedown(function (e) {
                        if (!e.target.className || e.target.className.indexOf('mtz-monthpicker') < 0) {
                            $this.monthpicker('hide');
                        }
                    });
                }
            });
        },



        show:function (n) {
             function showMPWidget(start_settings) {
                var widget = $('#' + start_settings.id);
                widget.find(".ui-mtz-picker-year-label").text(start_settings.year);
                selectedChanged(jQuery(widget.find('td[data-month=' + start_settings.month + ']'))[0]);
                widget.show();
            };

            var mp_data = this.data('monthpicker');
            showMPWidget(mp_data.settings_start);
            showMPWidget(mp_data.settings_end);

            $(this).parent().children(".month_date_picker_div").show();
        },

        hide:function () {
            $(this).parent().children(".month_date_picker_div").hide();
        },

        setValue:function (global_settings, settings_start, settings_end) {
            var month_start = format_month(global_settings, settings_start);
            var year_start = format_year(global_settings, settings_start);

            var month_end = format_month(global_settings, settings_end);
            var year_end = format_year(global_settings, settings_end);

            var date = format_date(global_settings, month_start, year_start, month_end, year_end);
            this.val(date);
        },

        mountMP:function () {
            var start_widget = $('#' + this.data('monthpicker').settings_start.id);
            var end_widget = $('#' + this.data('monthpicker').settings_end.id);
            var borderStart = jQuery('<div id="start_border" ></div>');
            var borderEnd = jQuery('<div id="end_border" ></div>');
            borderStart.append(start_widget);
            borderEnd.append(end_widget);
            $(this).parent().children(".month_date_picker_div").append(borderStart).append(borderEnd).hide();
        },

        mountWidget:function (global_settings, settings) {
            var
                monthpicker = this,
                container = $('<div id="' + settings.id + '" class="ui-datepicker ui-widget ui-widget-content ui-helper-clearfix ui-corner-all" />'),
                header = $('<div class="ui-datepicker-header ui-widget-header ui-helper-clearfix ui-corner-all mtz-monthpicker" />'),
                table = $('<table class = "mtz-monthpicker" />'),
                tbody = $('<tbody class = "mtz-monthpicker" />'),
                tr = $('<tr class = "mtz-monthpicker" / >'),
                td = '';

            var yearWidget = buildYearWidget(settings, monthpicker);

            option = null;

            container.css({
                whiteSpace:'nowrap',
                width:'210px',
                overflow:'hidden',
                textAlign:'center',
                display:'none'
            });

            header.append(yearWidget).appendTo(container);

            // mount months table
            for (var i = 1; i <= 12; i++) {
                td = $('<td class="ui-state-default mtz-monthpicker mtz-monthpicker-month" style="padding:5px;cursor:default;" />').attr('data-month', i);
                td.append(global_settings.monthNames[i - 1]);
                tr.append(td).appendTo(tbody);
                if (i % 3 === 0) {
                    tr = $('<tr class="mtz-monthpicker" />');
                }
            }

            table.append(tbody).appendTo(container);

            container.find('.mtz-monthpicker-month').bind('click', function () {
                var m = parseInt($(this).data('month'));
                settings.month = $(this).data('month');
                settings.monthName = $(this).text();
                monthpicker.trigger("monthpicker-click-month", $(this));
            });

            container.find('.mtz-monthpicker-year').bind('change', function () {
                settings.year = $(this).val();
                monthpicker.trigger('monthpicker-change-year', $(this).val());
            });

            container.appendTo('body');
        },

        destroy:function () {
            return this.each(function () {
                // TODO: look for other things to remove
                $(this).removeData('monthpicker');
            });
        }

    };

    $.fn.monthpicker = function (method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            methods.init.apply(this, arguments);
            return [jQuery("#start_border"), jQuery("#end_border")];
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.mtz.monthpicker');
        }
    };

    function format_month(global_settings, settings) {
        var month = settings.month;
        if (global_settings.pattern.indexOf('mmm') >= 0) {
            month = settings.monthName;
        } else if (global_settings.pattern.indexOf('mm') >= 0 && settings.month < 10) {
            month = '0' + settings.month;
        }
        return month;
    };

    function format_year(global_settings, settings) {
        var year;
        if (global_settings.pattern.indexOf('yyyy') < 0) {
            year = settings.year.toString().substr(2, 2);
        } else {
            year = settings.year;
        }
        return year;
    };

    function format_date(global_settings, month_start, year_start, month_end, year_end) {
        var date_start, date_end;

        if (global_settings.pattern.indexOf('y') > global_settings.pattern.indexOf(global_settings.dateSeparator)) {
            date_start = month_start + global_settings.dateSeparator + year_start;
            date_end = month_end + global_settings.dateSeparator + year_end;
        } else {
            date_start = year_start + global_settings.dateSeparator + month_start;
            date_end = year_end + global_settings.dateSeparator + month_end;
        }
        if(date_start == date_end) return date_start;
        return date_start + " - " + date_end;
    };

    function onYearChanged(combo_label, incredValue, cur_settings, monthpicker) {
        year = parseInt(combo_label.text()) - incredValue
        cur_settings.year = year + '';
        combo_label.text(cur_settings.year);

        setMPText(monthpicker);
    };

    function buildYearWidget(settings, monthpicker) {
        var
            combo = $('<div class="mtz-monthpicker mtz-monthpicker-year" /div>'),
            combo_pre = $('<a class="ui-datepicker-prev ui-corner-all " title="Prev"></a>'),
            combo_pre_span = $('<span class="ui-icon ui-icon-circle-triangle-w prev_year">Prev</span>'),
            combo_next = $('<a class="ui-datepicker-next ui-corner-all" title="Next"></a>'),
            combo_next_span = $('<span class="ui-icon ui-icon-circle-triangle-e next_year">Next</span>'),
            combo_label = $('<label class="ui-mtz-picker-year-label">' + settings.year + '</label>');

        combo_next.append(combo_next_span);
        combo_pre.append(combo_pre_span);
        combo.append(combo_next);
        combo.append(combo_pre);
        combo.append(combo_label);

        combo.find('.prev_year').bind('click', function(e){
            onYearChanged(combo_label, 1, settings, monthpicker);
        });
        combo.find('.next_year').bind('click', function (e) {
            onYearChanged(combo_label, -1, settings, monthpicker);
        });

        return combo;
    };


    function selectedChanged(element) {
        jQuery(element.parentNode.parentNode).find('.month-selected').removeClass('month-selected');
        jQuery(element).addClass('month-selected');
    };

})(jQuery);

function showMP(monthPicker) {
    var mp = monthPicker.parent().children(".month_date_picker_div");
    if (!mp.is(':visible')) {
        monthPicker.monthpicker('show');
    }
}

function setMPDates(monthpicker, start_year, start_month, end_year, end_month){
    var data = monthpicker.data('monthpicker');
    if(typeof data === 'undefined'){
        return;
    }
    data.settings_start.year = start_year;
    data.settings_start.month = start_month;
    data.settings_end.year = end_year;
    data.settings_end.month = end_month;
}

function setMPText(monthpicker) {
    if(typeof monthpicker.data('monthpicker') === 'undefined'){
        return;
    }
    var global_settings = monthpicker.data('monthpicker').settings,
        settings_start = monthpicker.data('monthpicker').settings_start,
        settings_end = monthpicker.data('monthpicker').settings_end;

    monthpicker.monthpicker('setValue', global_settings, settings_start, settings_end);
}

