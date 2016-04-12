"use strict";

import GenericQuestionForm from '../components/generic-question-form';

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
		{value: "geopoint", label: "Geopoint"}
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
			default:
				questionForm = null;
		}
		return questionForm;
	}
};
