import AppConstants from '../constants/app-constants';
import _ from 'lodash';

var requiredFieldRule = function (question) {
  let errors = {};

  let errorKey = question.name || question.temp_id || undefined;

  if (!errorKey) {
      return {};
  }

  _.forEach(AppConstants.REQUIRED_FIELDS, function (field) {
    if (!question[field]) {
      errors[errorKey] = errors[errorKey] || {};
      errors[errorKey][field] = AppConstants.CommonErrorMessages.REQUIRED_ERROR_MESSAGE;
    }
  });

  return errors;
}

module.exports = requiredFieldRule;
