import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';
import SampleQuestionnaire from '../store/sample-questionnaire';

var QuestionnaireActions = {
		initQuestionnaire : function(questionnaire_id){
			//call api and fetch questions
			
			AppDispatcher.dispatch({
				type: AppConstants.ActionTypes.INITIALIZE_QUESTIONNAIRE,
				questions : SampleQuestionnaire.questions
			});
			
		}
};

module.exports = QuestionnaireActions;