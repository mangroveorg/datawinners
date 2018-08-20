"use strict";

module.exports = {
	ActionTypes : {
		INITIALIZE_QUESTIONNAIRE: 'INITIALIZE_QUESTIONNAIRE',
		CREATE_QUESTION: 'CREATE_QUESTION',
		UPDATE_QUESTION: 'UPDATE_QUESTION',
		DELETE_QUESTION: 'DELETE_QUESTION',
		CREATE_CHOICE: 'CREATE_CHOICE',
		UPDATE_CHOICE: 'UPDATE_CHOICE',
		CREATE_CHOICE_GROUP: 'CREATE_CHOICE_GROUP',
		ERROR_ON_SAVE: 'ERROR_ON_SAVE',
		MOVE_UP: 'MOVE_UP',
		MOVE_DOWN: 'MOVE_DOWN'
	},
	CommonErrorMessages : {
		REQUIRED_ERROR_MESSAGE : 'This field is required',
		SAVE_FAILED: 'Save Failed',
		CLEAR_ALL_ERRORS: 'Clear all validation errors before saving the questionnaire'
	},
	LoaderMessages : {
		UPLOAD_MESSAGE: "Questionnaire being uploaded...",
		SAVE_MESSAGE: "Questionnaire being saved",
		TITLE_MESSAGE: "Please Wait...",
		SAVE_DRAFT_MESSAGE: "Questionnaire draft being saved"
	},
	GroupBoundaries : ['begin_group', 'begin_repeat', 'end_group', 'end_repeat'],
	MANDATORY_ASTERISK: '*',
	REQUIRED_QUESTION_FIELDS : ['label', 'name', 'type','choiceType'],
	REQUIRED_CHOICE_FIELDS : ['list_name', 'name', 'label'],
	QuestionnaireUrl : '/xlsform/',
	QuestionnaireSaveUrl : '/xlsform/',
	QuestionTypes : [
		{value: "text", label: "Text"},
		{value: "integer", label: "Integer"},
		{value: "decimal", label: "Decimal"},
		{value: "date", label: "Date"},
		{value: "geopoint", label: "Geopoint"},
		{value: "select_one", label:"Select one"},
		{value: "select_multiple", label:"Select multiple"},
		{value: "image", label: "Image"},
		{value: "audio", label: "Audio"},
		{value: "video", label: "Video"},
		{value: "dw_idnr", label: "Identification Number"},
		{value: "note", label: "Note"}
	],
	CHOICE_TYPE_FIELD_NAME :'choiceType',
	SELECT_QUESTION_TYPE : ['select_one','select_multiple']
};
