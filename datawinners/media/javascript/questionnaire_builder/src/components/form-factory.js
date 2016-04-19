import GenericQuestionForm from '../components/generic-question-form';
import SelectQuestionForm from '../components/select-question-form';
import _ from 'lodash';

module.exports = {
  getFormForQuestionType: function (questionType) {
    let type = _.split(questionType, ' ');
    var questionForm = null;
    switch(type[0]){
      case ''://For new question
      case 'text':
      case 'integer':
      case 'decimal':
      case 'date':
      case 'geopoint':
        questionForm = GenericQuestionForm;
        break;
      case 'select_one':
      case 'select_multiple':
        questionForm = SelectQuestionForm;
        break;
      default:
        questionForm = null;
    }
    return questionForm;
  }
};
