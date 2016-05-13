"use strict";

import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';
import QuestionnaireStore from '../store/questionnaire-store';
import Toastr from '../components/toastr';

var _persistData = (isDraft, callback) => {
	$.ajax({
		type: "POST",
		url: AppConstants.QuestionnaireSaveUrl+QuestionnaireStore.getQuestionnaireId()+'/',
		dataType: 'json',
		headers: { "X-CSRFToken": $.cookie('csrftoken') },
		data: {
					file_type:QuestionnaireStore.getFileType(),
					is_draft:isDraft,
						data:JSON.stringify(QuestionnaireStore.getQuestionnaire())
					}
	}).done(callback);
}

var QuestionnaireActions = {
		saveQuestionnaire : function (callback) {
			var onSaveHandler = (data) => {

				callback();
				if (data.status) {
					Toastr[data.status](data.details, data.reason);
				} else if (data.error_msg) {
					Toastr['error'](data.error_msg, data.message_prefix);
				}

				if(data.status == 'error' && data.errors) {
					AppDispatcher.dispatch({
						actionType: AppConstants.ActionTypes.ERROR_ON_SAVE,
						data: data.errors
					});
				} else {
					QuestionnaireActions.initQuestionnaire(QuestionnaireStore.getQuestionnaireId(), 'true');
				}

			}

			if (QuestionnaireStore.errorsPresent()) {
				callback();
				Toastr['error'](AppConstants.CommonErrorMessages.CLEAR_ALL_ERRORS, AppConstants.CommonErrorMessages.SAVE_FAILED);
				return;
			}

			_persistData(false, onSaveHandler);

		},

		initQuestionnaire: function(questionnaire_id, reload){
			let url = AppConstants.QuestionnaireUrl + questionnaire_id + '/';
			var self = this;
			this.serverRequest = $.ajax({
					url: url,
					data: {reload:reload},
					dataType: 'json',
					success: function (result) {
						QuestionnaireStore.loadQuestionnaireId(questionnaire_id);
						QuestionnaireStore.loadFileType(result.file_type);
						QuestionnaireStore.loadQuestionnaire(result.questionnaire);
						QuestionnaireStore.loadUniqueIdTypes(result.unique_id_types);
						QuestionnaireStore.loadInitErrors(result.reason, result.details);
						AppDispatcher.dispatch({
							actionType: AppConstants.ActionTypes.INITIALIZE_QUESTIONNAIRE
						});

					}
				});

		},
		createQuestion: function (question_type) {
			var new_question_type = question_type || ''; //Default question type
			let new_question = {};
			for (var field of QuestionnaireStore.questionFields()) {
				new_question[field] = '';
			}
			new_question['type'] = new_question_type;
			new_question['isNewQuestion'] = true;
			new_question['isSupported'] = true;
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

		moveUp: function(question) {
			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.MOVE_UP,
				data: {question: question}
			});
		},

		moveDown: function(question) {
			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.MOVE_DOWN,
				data: {question: question}
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
		},

		saveDraft: function(callback){
		  let questionnaire = QuestionnaireStore.getQuestionnaire();
			var onSaveDraftHandler = (data) => {
					callback();
					if (data.status) {
						Toastr[data.status](data.details, data.reason);
					} else if (data.error_msg) {
						Toastr['error'](data.error_msg, data.message_prefix);
					}
			}
			_persistData(true, onSaveDraftHandler);
		}
};

module.exports = QuestionnaireActions;
