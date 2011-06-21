$(document).ready(function() {
    $('#autogen').unbind('change').change(function(event) {
        if ($('#autogen').attr('checked') != true) {
            $('#short_name').attr('disabled', '');

        }
        else {
            $('#short_name').removeClass('error');
            $("#short_name").parent().find('label.error').hide();
            $('#short_name').val("");
            DW.viewModel.message.s('')
            $('#short_name').attr('disabled', 'disabled');
        }
    });

    $.validator.addMethod('regexrule', function(value, element, params) {
        var text = $('#' + element.id).val().trim();
        if (text=="")
            return true;
        var re = new RegExp("^[0-9]+(\-[0-9]+)*$");
        return re.test(text);
    }, "Please enter a valid phone number");

    $.validator.addMethod('gpsrule', function(value, element, params) {
        var codes = $('#' + element.id).val();
        codes = codes.trim();
        if (codes == "")
            return true;
        codes = codes.replace(/\s+/g, " ");
        lat_long = codes.split(' ');

        if (lat_long.length != 2)
            return false;
        return (lat_long[0] > -90 && lat_long[0] < 90)
                && (lat_long[1] > -180 && lat_long[1] < 180);
    }, "Incorrect GPS coordinates. Please resubmit");

    DW.validator = $('#question_form').validate({
        messages:{
            geo_code:{
                required:"Required information for registration. Please fill out at least one location field."
            },
            location:{
                required:"Required information for registration. Please fill out at least one location field"
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
                    return $("#location").val().trim() == "";
                },
                gpsrule: true
            },
            location:{
                required:function(element) {
                    return $("#geo_code").val().trim() == "";
                }
            },
            short_name:{
                required :true
            }
        }
    });


});