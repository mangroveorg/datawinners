import TextQuestionForm from '../components/text-question-form';
import IntegerQuestionForm from '../components/integer-question-form';
import DateQuestionForm from '../components/date-question-form';
import DecimalQuestionForm from '../components/decimal-question-form';
import NoteQuestionForm from '../components/note-question-form';


module.exports = {
	ActionTypes : {
		INITIALIZE_QUESTIONNAIRE: 'INITIALIZE_QUESTIONNAIRE',
		CREATE_QUESTION: 'CREATE_QUESTION',
		UPDATE_QUESTION: 'UPDATE_QUESTION',
		DELETE_QUESTION: 'DELETE_QUESTION'
	},
	QuestionnaireUrl : '/xlsform/',
	// QuestionnaireUrl : '/project/questionnaire/ajax/',
	QuestionnaireSaveUrl : '/xlsform/upload/update/',
	QuestionTypeSupport : {
	  text : TextQuestionForm,
	  date : DateQuestionForm,
	  integer : IntegerQuestionForm,
	  decimal : DecimalQuestionForm,
		note : NoteQuestionForm
	},
	//TODO: this should be clubed with QuestionTypeSupport object
	QuestionTypesDropdown : [
	  "Text", "Integer", "Decimal", "Note", "Date",
	  "Time", "Location", "Select one", "Select multiple",
	  "Calculate"
	]
}
