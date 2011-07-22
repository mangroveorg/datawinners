$(document).ready(function() {

     $("#location").autocomplete("/places", {
        minChars: 0,
        max: 12,
        autoFill: true,
        mustMatch: true,
        matchContains: false,
        scrollHeight: 220});

    $.validator.addMethod('regexrule', function(value, element, params) {
        var text = $.trim($('#' + element.id).val());
        if (text=="")
            return true;
        var re = new RegExp("^[^a-zA-Z]*$");
        return re.test(text);
    }, "Please enter a valid phone number");

    $.validator.addMethod('gpsrule', function(value, element, params) {
        var codes = $('#' + element.id).val();
        codes = $.trim(codes);
        if (codes == "")
            return true;
        codes = codes.replace(/\s+/g, " ");
        lat_long = codes.split(' ');

        if (lat_long.length != 2)
            return false;
        return (lat_long[0] > -90 && lat_long[0] < 90)
                && (lat_long[1] > -180 && lat_long[1] < 180);
    }, "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315");

    DW.validator = $('#question_form').validate({
        messages:{
            geo_code:{
                required:"Please fill out at least one location field."
            },
            location:{
                required:"Please fill out at least one location field"
            }

        },
        rules:{
            entity_name:{
                required: true
            },

            mobile_number:{
                regexrule:true

            },
            geo_code:{
                required:function(element) {
                    return $.trim($("#id_location").val()) == "";
                },
                gpsrule: true
            },
            location:{
                required:function(element) {
                    return $.trim($("#geo_code").val()) == "";
                }
            },
            short_name:{
                required :true
            }
        },
        wrapper: "label",
        errorPlacement: function(error, element) {
                    offset = element.offset();
                    error.insertAfter(element)
                    error.addClass('error_arrow');  // add a class to the wrapper

        }
});


});