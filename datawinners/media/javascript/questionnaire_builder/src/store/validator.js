import AppConstants from '../constants/app-constants';
import Rules from '../rules/rules';
import _ from 'lodash';

var validateQuestionnaire = function (questionnaire) {
  let errors = [];
  _.forEach(questionnaire.survey, function (question) {
    errrors = _.concate(errors, validateQuestion(question));
  });
  return errors;
};

var validateQuestion = function (question) {
  let errors = [];
  _.forEach(Rules.SurveyRules, function (rule) {
      errors.push(rule(question));
    });
  return errors;
};

module.exports = {
                    validateQuestion : validateQuestion,
                    validateQuestionnaire : validateQuestionnaire
                 };
