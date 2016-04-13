"use strict";

import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';
import SampleQuestionnaire from '../store/sample-questionnaire';
import Toastr from 'toastr';
import _ from 'lodash';

var findQuestionIndex = function(survey, question) {
	let index = _.findIndex(survey, {temp_id: question.temp_id});
	if(index < 0){
		index = _.findIndex(survey, {name: question.name});
	}
	return index;
};

var QuestionnaireActions = {
		saveQuestionnaire : function(id, questionnaire, file_type){
			var onSaveHandler = (data) => {
				Toastr[data.status](data.details, data.reason);
			}
			$.ajax({
			  type: "POST",
			  url: AppConstants.QuestionnaireSaveUrl+id+'/',
				dataType: 'json',
				headers: { "X-CSRFToken": $.cookie('csrftoken') },
			  data: {
							file_type:file_type,
								data:JSON.stringify(questionnaire)
							}
			}).done(onSaveHandler);
		},

		createQuestion: function(questionnaire, question_type) {
			var new_question_type = 'text' //Default question type
			if(question_type){
					new_question_type = question_type;
			}
			let question_fields = Object.keys(questionnaire.survey[0]);
			let new_question = {};
			for (var field of question_fields) {
				new_question[field]='';
			}
			new_question['type']=new_question_type;
			new_question['isNewQuestion']=true;
			new_question['temp_id']=Math.random();

			questionnaire.survey.push(new_question);

			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.CREATE_QUESTION,
				questionnaire: questionnaire
			});
		},

		updateQuestion: function(questionnaire, question) {

			questionnaire.survey[findQuestionIndex(questionnaire.survey, question)] = question;

			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.UPDATE_QUESTION,
				questionnaire: questionnaire
			});
		},

		deleteQuestion: function(questionnaire, question) {
			questionnaire.survey.splice([findQuestionIndex(questionnaire.survey, question)], 1);
			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.DELETE_QUESTION,
				questionnaire: questionnaire
			});
		}

};

module.exports = QuestionnaireActions;
