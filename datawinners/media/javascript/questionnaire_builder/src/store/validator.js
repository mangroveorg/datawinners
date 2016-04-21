import AppConstants from '../constants/app-constants';
import Rules from '../rules/rules';
import _ from 'lodash';


var validateQuestionnaire = function (questionnaire) {
  let errors = [];
  _.forEach(questionnaire.survey, function (question) {
      let errorsForQuestion = validateQuestion(question);
      if (!_.isEmpty(errorsForQuestion)) {
        errors = _.concat(errors, errorsForQuestion);
      }
  });
  return _.compact(errors);
};

var validateQuestion = function (question) {
  let errors = [];
  if(question.isSupported){
    _.forEach(Rules.SurveyRules, function (rule) {
        let errorsForQuestion = rule(question);
        if (!_.isEmpty(errorsForQuestion)) {
          errors.push(errorsForQuestion);
        }
      });
  }
  return errors;
};

module.exports = {
                    validateQuestion : validateQuestion,
                    validateQuestionnaire : validateQuestionnaire
                 };
