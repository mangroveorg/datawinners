import GenericQuestionForm from '../components/generic-question-form';
import SelectQuestionForm from '../components/select-question-form';
import UniqueIdQuestionForm from '../components/unique-id-question-form';
import _ from 'lodash';

module.exports = {
  getFormForQuestionType: function (questionType) {
    let type = _.split(questionType, ' ');
    var questionForm;
    switch(type[0]){
      case ''://For new question
      case 'text':
      case 'integer':
      case 'decimal':
      case 'date':
      case 'geopoint':
      case 'image':
      case 'audio':
      case 'video':
        questionForm = GenericQuestionForm;
        break;
      case 'select_one':
      case 'select_multiple':
        questionForm = SelectQuestionForm;
        break;
      case 'dw_idnr':
        questionForm = UniqueIdQuestionForm;
        break;
      default:
        //do nothing
    }
    return questionForm;
  }
};
