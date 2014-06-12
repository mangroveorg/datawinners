DW = DW || {};
DW.ko = {
        createValidatableObservable: function(options){
                var defaults = {value: "", valid: true, error: ""};
                var params = $.extend({}, defaults, options);

                var observable = ko.observable(params.value);
                observable.valid = ko.observable(params.valid);
                observable.error = ko.observable(params.error);
                observable.clearError = function(){
                  this.valid(true);
                  this.error("");
                };
                observable.setError = function(message){
                  this.valid(false);
                  this.error(message);
                };
                return observable;
            },
        createValidatableObservableObject: function(options){
                var defaults = {value: [], valid: ko.observable(true), error: ko.observable("")};
                var observable = $.extend({}, defaults, options);
                observable.clearError = function(){
                  this.valid(true);
                  this.error("");
                };
                observable.setError = function(message){
                  this.valid(false);
                  this.error(message);
                };
                return observable;
            },
        mandatoryValidator: function(observable,error_message){
            if(observable() == undefined || (observable()+ "").trim() === "" ){
                observable.setError(error_message|| gettext("This field is required."))
                return false;
            }
            else
                observable.clearError();
            return true;
        },
        numericValidator: function(observable){
             if(!observable() || (observable()+"").match(/^-?\d+$/)){
                observable.clearError();
                return true;
             } else {
                 observable.setError(gettext("Please insert a valid number."));
                return false;
            }
        },
        postiveNumberValidator: function(observable){
            this.numericValidator(observable);
            if(observable.valid()){
                if(parseInt(observable()) <= 0) {
                    observable.setError(gettext("Please insert a valid number."));
                    return false;
                } else {
                    observable.clearError();
                    return true;
                }
            }
        },
        alphaNumericValidator: function(observable, trimBeforeCheck){
            var str = trimBeforeCheck ? (observable() + "").trim() : observable() + "";
            if(str.match(/^[0-9a-zA-Z]+$/)) {
                observable.clearError();
                return true;
            } else {
                observable.setError(gettext("Only letters and digits are valid"));
                return false;
            }
        },customValidator: function(observable,error_message, validator){
            var val = observable();
            if(!validator(val)){
                observable.setError(gettext(error_message)|| gettext("This field is required."))
                return false;
            }
            else {
                observable.clearError();
                return true;
            }
        }
};
