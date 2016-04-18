"use strict";

import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';
import QuestionnaireStore from '../store/questionnaire-store';
import Toastr from 'toastr';

var QuestionnaireActions = {
		saveQuestionnaire : function (id, questionnaire, file_type) {
			var onSaveHandler = (data) => {
				if (data.status) {
					Toastr[data.status](data.details, data.reason);
				} else if (data.error_msg) {
					Toastr['error'](data.error_msg, data.message_prefix);
				}
				AppDispatcher.dispatch({
					actionType: AppConstants.ActionTypes.ERROR_ON_SAVE,
					data: data.errors
				});

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
			var new_question_type = question_type || ''; //Default question type
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
		},

		updateChoice: function(choice) {
			QuestionnaireStore.updateChoice(choice);
			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.UPDATE_CHOICE
			});
		},

		deleteChoice: function(base_index) {
			QuestionnaireStore.deleteChoice(base_index);
			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.DELETE_CHOICE
			});
		},

		createChoice: function(choiceGroupName, added_field, value) {
			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.CREATE_CHOICE,
				data:{
					choiceGroupName:choiceGroupName,
					added_field: added_field,
					value: value
				}
			});
		},

		createChoiceGroup: function(){
			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.CREATE_CHOICE_GROUP
			});
		}

};

module.exports = QuestionnaireActions;
