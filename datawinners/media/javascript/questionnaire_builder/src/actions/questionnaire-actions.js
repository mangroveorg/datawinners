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
			let choice = {};
			for (let required_field in QuestionnaireStore.choiceFields){
				choice[required_field] = '';
			}
			choice[added_field]=value;
			choice['list name'] = choiceGroupName;

			QuestionnaireStore.createChoice(choice);
			AppDispatcher.dispatch({
				actionType: AppConstants.ActionTypes.CREATE_CHOICE
			});
		}

};

module.exports = QuestionnaireActions;
