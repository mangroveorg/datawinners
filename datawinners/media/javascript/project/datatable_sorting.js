

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
    }

} );

function compareNumber(a, b) {
    return ((a < b) ? -1 : ((a > b) ? 1 : 0));
};