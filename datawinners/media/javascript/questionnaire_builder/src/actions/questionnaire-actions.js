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

		createQuestion: function(question) {
			var newQuestion = question//TODO

			Dispatcher.dispatch({
				actionType: AppConstants.CREATE_QUESTION,
				question: newQuestion
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
