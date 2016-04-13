import GenericQuestionForm from '../components/generic-question-form';
import SelectQuestionForm from '../components/select-question-form';

module.exports = {
  getFormForQuestionType: function (type) {
    var questionForm = null;
    switch(type){
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
