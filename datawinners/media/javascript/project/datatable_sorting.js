

jQuery.extend( jQuery.fn.dataTableExt.oSort, {
    "mm.yyyy-pre": function ( a ) {
        var ukDatea = a.split('.');
        return ukDatea[0]*1 + ukDatea[1]* 12;
    },

    "mm.yyyy-asc": function ( a, b ) {
        a = jQuery.fn.dataTableExt.oSort["mm.yyyy-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["mm.yyyy-pre"](b);
        return compareNumber(a, b);
    },

    "mm.yyyy-desc": function ( a, b ) {
        a = jQuery.fn.dataTableExt.oSort["mm.yyyy-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["mm.yyyy-pre"](b);
        return compareNumber(b, a);
    },

    "mm.dd.yyyy-pre": function ( a ) {
        var ukDatea = a.split('.');
        return ukDatea[1]*1 + ukDatea[0]*31 + ukDatea[2]* 31 * 12;
    },

    "mm.dd.yyyy-asc": function ( a, b ) {
        a = jQuery.fn.dataTableExt.oSort["mm.dd.yyyy-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["mm.dd.yyyy-pre"](b);
        return compareNumber(a, b);
    },

    "mm.dd.yyyy-desc": function ( a, b ) {
        a = jQuery.fn.dataTableExt.oSort["mm.dd.yyyy-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["mm.dd.yyyy-pre"](b);
        return compareNumber(b, a);
    },

    "dd.mm.yyyy-pre": function ( a ) {
        var ukDatea = a.split('.');
        return ukDatea[0]*1 + ukDatea[1]*31 + ukDatea[2]* 31 * 12;
    },

    "dd.mm.yyyy-asc": function ( a, b ) {
        a = jQuery.fn.dataTableExt.oSort["dd.mm.yyyy-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["dd.mm.yyyy-pre"](b);
        return compareNumber(a, b);
    },

    "dd.mm.yyyy-desc": function ( a, b ) {
        a = jQuery.fn.dataTableExt.oSort["dd.mm.yyyy-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["dd.mm.yyyy-pre"](b);
        return compareNumber(b, a);
    },

    "gps-pre": function ( a ) {
        var cords = a.match(/[-0-9.]+/gi);
        return [cords[0]*1, cords[1]*1]
    },

    "gps-asc": function ( a, b ) {
        a = jQuery.fn.dataTableExt.oSort["gps-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["gps-pre"](b);
        var xCompare = compareNumber(a[0], b[0]);
        if (xCompare == 0) return compareNumber(a[1], b[1])
        return xCompare
    },

    "gps-desc": function ( a, b ) {
        a = jQuery.fn.dataTableExt.oSort["gps-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["gps-pre"](b);
        var xCompare = compareNumber(b[0], a[0]);
        if (xCompare == 0) return compareNumber(b[1], a[1])
        return xCompare
    },

    "submission_date-pre": function (a) {
        var ukDatea = a.split(" ");
        var months = [ "",
            gettext("Jan."),
            gettext("Feb."),
            gettext("Mar."),
            gettext("Apr."),
            gettext("May."),
            gettext("Jun."),
            gettext("Jul."),
            gettext("Aug."),
            gettext("Sep."),
            gettext("Oct."),
            gettext("Nov."),
            gettext("Dec.")
        ];
        var month = $.inArray(gettext(ukDatea[0]), months) * 31 * 24 * 60;
        var day = parseInt(ukDatea[1]) * 24 * 60;
        var year = parseInt(ukDatea[2]) * 12 * 31 * 24 * 60;
        var hh_mm = ukDatea[3].split(":");
        var hour = (parseInt(hh_mm[0]) + ((ukDatea[4] == "PM") ? 12 : 0)) * 60;
        var minute = parseInt(hh_mm[1]);
        return month + day + year + hour + minute;
    },

    "submission_date-asc": function (a, b){
        a = jQuery.fn.dataTableExt.oSort["submission_date-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["submission_date-pre"](b);
        return compareNumber(a, b);
    },

    "submission_date-desc": function (a, b){
        a = jQuery.fn.dataTableExt.oSort["submission_date-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["submission_date-pre"](b);
        return compareNumber(b, a);
    },

    "reporting_period-pre": function (a){
        var ukDatea = a.split(".");

        if (ukDatea.length == 2) {
            ukDatea = get_month_last_day(ukDatea);
        } else {
            ukDatea = get_dd_mm_yyyy_values(ukDatea);
        }

        return jQuery.fn.dataTableExt.oSort["dd.mm.yyyy-pre"](ukDatea.join("."));
    },

    "reporting_period-asc": function (a, b){
        a = jQuery.fn.dataTableExt.oSort["reporting_period-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["reporting_period-pre"](b);
        return compareNumber(a, b);
    },

    "reporting_period-desc": function (a, b){
        a = jQuery.fn.dataTableExt.oSort["reporting_period-pre"](a);
        b = jQuery.fn.dataTableExt.oSort["reporting_period-pre"](b);
        return compareNumber(b, a);
    }

} );

function compareNumber(a, b) {
    return ((a < b) ? -1 : ((a > b) ? 1 : 0));
};

function get_month_last_day(mm_yyyy) {
    var d = new Date();
    d.setFullYear(mm_yyyy[1], mm_yyyy[0], 0);
    return [d.getDate(), mm_yyyy[0], mm_yyyy[1]];
}

function get_dd_mm_yyyy_values(datea) {
    var date_format = window.date_format;

    if (typeof(date_format) == 'undefined') {
        var date_format = 'dd.mm.yyyy';
    }

    if ((datea[1] > 12) || ((datea[0] <= 12) && (date_format == 'mm.dd.yyyy'))){
        return [datea[1], datea[0], datea[2]];
    }

    return datea;
}