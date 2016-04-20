import AppConstants from '../constants/app-constants';
import _ from 'lodash';

//TODO: need to cascade & choice rules when needed
var RULES = {},
    SURVEY_RULES = [];

function setup () {
  SURVEY_RULES.push(requiredFieldRule);
  RULES.SurveyRules = SURVEY_RULES;
}

//TODO Extract rule into separate file when needed
var requiredFieldRule = function (question) {
  let errors = {};

  let errorKey = question.name || question.temp_id || undefined;

  if (!errorKey) {
      return {};
  }

  errors[errorKey] = errors[errorKey] || {};
  _.forEach(AppConstants.REQUIRED_FIELDS, function (field) {
    if (!question[field]) {
      errors[errorKey][field] = AppConstants.CommonErrorMessages.REQUIRED_ERROR_MESSAGE;
    }
  });

  return errors;
}

var validateQuestionnaire = function (questionnaire) {
  let errors = [];
  _.forEach(questionnaire.survey, function (question) {
    errrors = _.concate(errors, validateQuestion(question));
  });
  return errors;
};

var validateQuestion = function (question) {
  let errors = [];
  _.forEach(RULES.SurveyRules, function (rule) {
      errors.push(rule(question));
    });
  return errors;
};

setup();

module.exports = {
                    validateQuestion : validateQuestion,
                    validateQuestionnaire : validateQuestionnaire
                 };
