"use strict";

import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';
import QuestionnaireStore from '../store/questionnaire-store';
import Toastr from 'toastr';

var QuestionnaireActions = {
		saveQuestionnaire : function (id, questionnaire, file_type) {
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

		createQuestion: function (question_type) {
			var new_question_type = question_type || 'text'; //Default question type
			let new_question = {};
			for (var field of QuestionnaireStore.questionFields()) {
				new_question[field] = '';
			}
			new_question['type'] = new_question_type;
			new_question['isNewQuestion'] = true;
			new_question['temp_id'] = Math.random();
			QuestionnaireStore.add(new_question);
			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.CREATE_QUESTION
			});
		},

		updateQuestion: function (question) {
			QuestionnaireStore.update(question);
			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.UPDATE_QUESTION
			});
		},

		deleteQuestion: function (question) {
			QuestionnaireStore.delete(question);
			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.DELETE_QUESTION
			});
		}

};

module.exports = QuestionnaireActions;
