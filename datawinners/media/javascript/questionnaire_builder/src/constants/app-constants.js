import TextQuestionForm from '../components/textQuestionForm';
import IntegerQuestionForm from '../components/integerQuestionForm';
import DateQuestionForm from '../components/dateQuestionForm';
import DecimalQuestionForm from '../components/decimalQuestionForm';


module.exports = {
	ActionTypes : {
		INITIALIZE_QUESTIONNAIRE: 'INITIALIZE_QUESTIONNAIRE',
		CREATE_QUESTION: 'CREATE_QUESTION',
		UPDATE_QUESTION: 'UPDATE_QUESTION',
		DELETE_QUESTION: 'DELETE_QUESTION'
	},
	QuestionnaireUrl : '/project/questionnaire/ajax/',
	QuestionTypeSupport : {
	  text : TextQuestionForm,
	  date : DateQuestionForm,
	  integer : IntegerQuestionForm,
	  decimal : DecimalQuestionForm
	}
}
