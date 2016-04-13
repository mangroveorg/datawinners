import {EventEmitter} from 'events';

const CHANGE_EVENT = 'change';
// import SampleQuestionnaire from './sample-questionnaire';
import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';

var QuestionnaireStore = Object.assign({},EventEmitter.prototype, {
	questionnaire: {},

	addChangeListener: function(callback) {
		this.on(CHANGE_EVENT,callback);
	},

	removeChangeListener:function(callback){
		this.removeListener(CHANGE_EVENT, callback);
	},

	emitChange: function(){
		this.emit(CHANGE_EVENT)
	},

	getQuestionnaire: function(){
		return this.questionnaire;
	}

});

AppDispatcher.register(function(action){
	switch (action.actionType){
		//TODO: this needs to be updated
		case AppConstants.ActionTypes.UPDATE_QUESTION:
		case AppConstants.ActionTypes.CREATE_QUESTION:
		case AppConstants.ActionTypes.DELETE_QUESTION:
			QuestionnaireStore.questionnaire = action.questionnaire;
			QuestionnaireStore.emitChange();
			break;
		default:
			//do nothing
	}
});

module.exports = QuestionnaireStore;
