import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';
import SampleQuestionnaire from '../store/sample-questionnaire';

var QuestionnaireActions = {
		// initQuestionnaire : function(questionnaire_id){
		// 	//call api and fetch questions
		//
		// 	AppDispatcher.dispatch({
		// 		type: AppConstants.ActionTypes.INITIALIZE_QUESTIONNAIRE,
		// 		questions : SampleQuestionnaire.questions
		// 	});
		//
		// },

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
