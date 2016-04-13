"use strict";

import GenericQuestionForm from '../components/generic-question-form';
import SelectQuestionForm from '../components/select-question-form';

module.exports = {
	ActionTypes : {
		INITIALIZE_QUESTIONNAIRE: 'INITIALIZE_QUESTIONNAIRE',
		CREATE_QUESTION: 'CREATE_QUESTION',
		UPDATE_QUESTION: 'UPDATE_QUESTION',
		DELETE_QUESTION: 'DELETE_QUESTION'
	},
	QuestionnaireUrl : '/xlsform/',
	QuestionnaireSaveUrl : '/xlsform/',
	QuestionTypes : [
		{value: "text", label: "Text"},
		{value: "integer", label: "Integer"},
		{value: "decimal", label: "Decimal"},
		{value: "date", label: "Date"},
		{value: "geopoint", label: "Geopoint"},
		{value: "select_one", label:"Select one"},
		{value: "select_multiple", label:"Select multiple"}
	],
	getFormForQuestionType: function(type){
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
