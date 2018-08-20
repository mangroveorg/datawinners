import AppConstants from '../constants/app-constants';
import _ from 'lodash';

var requiredFieldRule = function (question) {
    let errors = {};

    let errorKey = question.temp_id || question.name || undefined;

    if (!errorKey) {
        return {};
    }
    let questionTypes = _.split(question.type,' ');
    _.forEach(AppConstants.REQUIRED_QUESTION_FIELDS, function (field) {
        if(field == AppConstants.CHOICE_TYPE_FIELD_NAME){
            if(AppConstants.SELECT_QUESTION_TYPE.indexOf(questionTypes[0]) != -1){
                if(!questionTypes[1] || questionTypes[1].length == 0){
                    errors[errorKey] = errors[errorKey] || {};
                    errors[errorKey][field] = AppConstants.CommonErrorMessages.REQUIRED_ERROR_MESSAGE;
                }
            }
        }
        else{
            if (!question[field]) {
                errors[errorKey] = errors[errorKey] || {};
                errors[errorKey][field] = AppConstants.CommonErrorMessages.REQUIRED_ERROR_MESSAGE;
            }
        }
    });

    return errors;
}

module.exports = requiredFieldRule;
