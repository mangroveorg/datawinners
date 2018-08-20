import RequiredFieldRule from './required-field-rule'
import RequiredChoiceRule from './required-choice-rule'

//TODO Add rules for choice & cascade

module.exports = {
  SurveyRules: [RequiredFieldRule],
  ChoiceRules: [RequiredChoiceRule],
  CascadeRules: []
};
