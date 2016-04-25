import AppConstants from '../constants/app-constants';
import _ from 'lodash';

var requiredChoiceRule = function (choice) {
  let errors = {};

  let errorKey = choice.base_index;

  _.forEach(AppConstants.REQUIRED_CHOICE_FIELDS, function (field) {
    if (!choice[field]) {
      errors[errorKey] = errors[errorKey] || {};
      errors[errorKey][field] = AppConstants.CommonErrorMessages.REQUIRED_ERROR_MESSAGE;
    }
  });
  console.log(errors);
  return errors;
}

module.exports = requiredChoiceRule;
