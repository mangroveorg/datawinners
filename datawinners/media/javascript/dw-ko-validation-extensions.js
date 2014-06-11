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
        mandatoryValidator: function(observable){
            if(observable() == undefined || (observable()+ "").trim() === "" )
                observable.setError(gettext("This field is required."))
            else
                observable.clearError();
        },
        numericValidator: function(observable){
             if(!observable() || (observable()+"").match(/^-?[0-9]+/))
                observable.clearError();
             else
                observable.setError(gettext("Please insert a valid number."));
        },
        postiveNumberValidator: function(observable){
            this.numericValidator(observable);
            if(observable.valid()){
                if(parseInt(observable()) <= 0)
                    observable.setError(gettext("Please insert a valid number."));
                else
                    observable.clearError();
            }
        },
        alphaNumericValidator: function(observable, trimBeforeCheck){
            var str = trimBeforeCheck ? (observable() + "").trim() : observable() + "";
            if(str.match(/^[0-9a-zA-Z]+$/))
                observable.clearError();
             else
                observable.setError(gettext("Only letters and digits are valid"));
        }
};
