DW.broadcast_sms=function(){
    this.clearElementId='#clear_broadcast_sms_form';
    this.formElementId="#broadcast_sms_form";
    this.idToElement="#id_to";
    this.messageCountElement="#messageCount";
    this.smsContentElement="#sms_content";
    this.maxSMSChar=160;
    this.additional_column=new DW.additional_column();

};

DW.broadcast_sms.prototype={
    init:function(){
        this.createSMSContentValidationRule();
        this.createAdditionalTelephoneValidationRule();
        this.additional_column.hide();
        this.setMessageCount();
    },

    createAdditionalTelephoneValidationRule:function(){
        this.additional_column.createAdditionalTelephoneValidationRule();
    },
    createSMSContentValidationRule:function(){
        var defaults = $(this.formElementId).validate({
            rules: {
                text:{
                    required:true
                }
            },
            wrapper: "div",
            errorPlacement: function(error, element) {
                error.insertAfter(element);
                error.addClass('error_arrow');  // add a class to the wrapper
            }
        });

    },

    processAddtionalColumnValidation:function(){
        if (this.isAdditionalSelected()) {
            this.additional_column.processSelected();
        }
        else {
            this.additional_column.processUnSelected();
        }
    },

    isAdditionalSelected:function(){
        return $(this.idToElement).val() == "Additional";
    },
    setMessageCount:function(){
        $(this.messageCountElement).html("<b>"+ this.getSMSLength() + "</b> of "+this.maxSMSChar);
    },
    getSMSLength:function(){
        return $(this.smsContentElement).val().length;
    },
    clearContent:function(){
        $(this.smsContentElement).val("");
        $(this.additional_column.telephoneNumbersElementId).val("");
        $("#broadcast_sms_form label.error").each(function(){
            $(this).remove();
        });
        this.setMessageCount();
    },
    getSMSContent:function(){
        return $(this.smsContentElement).val()
    },
    limitCount:function () {
        if (this.getSMSLength() > this.maxSMSChar){
            $(this.smsContentElement).val(this.getSMSContent().substring(0, this.maxSMSChar));
        }
        this.setMessageCount();
    }
};


DW.additional_column=function(){
    this.additionalPeopleId="#additional_people_column";
    this.telephoneNumbersElementId='#id_others';
    this.telephone_number_rule="regexrule";
};

DW.additional_column.prototype={
    createAdditionalTelephoneValidationRule:function(){
        $.validator.addMethod(this.telephone_number_rule, function(value, element) {
            var text = $('#' + element.id).val();
            var re = new RegExp('^[0-9 ,]+$');
            var string_has_non_numeric_char = re.test(text);
            if (!string_has_non_numeric_char){
                return false;
            }
            var telephone_numbers = text.split(',');
            var each;
            var invalid = [];
            var telephone_number = "";
            for (each in telephone_numbers) {
                telephone_number = telephone_numbers[each].trim();
                if (telephone_number.length > DW.digits_number_limit){
                    invalid.push(telephone_number);
                }
            }
            if (invalid.length) {
                $("#id_others").highlightTextarea('setWords', invalid);
                return false;
            }
            return true;
        }, interpolate(gettext("Enter local telephone number of %(limit)s digits or less"), {limit: DW.digits_number_limit}, true));
    },

    addRule:function(){
        $(this.telephoneNumbersElementId).rules("add", this.telephone_number_rule);
        $(this.telephoneNumbersElementId).rules("add", "required");

    },
    show:function(){
        $(this.additionalPeopleId).removeClass('none');
    },
    hide:function(){
        $(this.additionalPeopleId).addClass('none');
    },
    removeRule:function(){
        $(this.telephoneNumbersElementId).rules("remove", this.telephone_number_rule);
        $(this.telephoneNumbersElementId).rules("remove", "required");
    },
    processSelected:function(){
        this.addRule();
        this.show();

    },
    processUnSelected:function(){
        this.removeRule();
        this.hide();
        $(this.telephoneNumbersElementId).val("");
        $(this.telephoneNumbersElementId).valid();

    }
};


DW.getDigitsNumberLimit = function(){
    if (DW.ong_country == "NG") {
        return 11;
    }
    return 10;
};

$(document).ready(function() {
    DW.digits_number_limit = DW.getDigitsNumberLimit();
    var broadcast_sms=new DW.broadcast_sms();
    broadcast_sms.init();

    $(broadcast_sms.smsContentElement).keyup(function() {
        broadcast_sms.limitCount();
    });

    $(broadcast_sms.smsContentElement).keydown(function() {
        broadcast_sms.limitCount();
    });

    $('#id_to').change(function() {
        broadcast_sms.processAddtionalColumnValidation();
    });

    $('#clear_broadcast_sms_form').click(function() {
        broadcast_sms.clearContent();
    });
});