"use strict";

import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';
import SampleQuestionnaire from '../store/sample-questionnaire';
import Toastr from 'toastr';

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

		updateQuestion: function(question) {
			var updatedQuestion = question//TODO

			Dispatcher.dispatch({
				actionType: AppConstants.UPDATE_QUESTION,
				question: updatedQuestion
			});
		},

		deleteQuestion: function(id) {
			//TODO

			Dispatcher.dispatch({
				actionType: AppConstants.DELETE_QUESTION,
				id: id
			});
		}

};

module.exports = QuestionnaireActions;
