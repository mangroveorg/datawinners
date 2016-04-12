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
		case AppConstants.ActionTypes.INITIALIZE_QUESTIONNAIRE:
			QuestionnaireStore.questions = action.questions;
			QuestionnaireStore.emitChange();
		case AppConstants.ActionTypes.CREATE_QUESTION:
			QuestionnaireStore.questionnaire = action.questionnaire;
			QuestionnaireStore.emitChange();
		default:
			//do nothing
	}
});

/*
//Inheritance based store
class QuestionnaireStore extends EventEmitter{
	constructor(){
		super();
//		this.questionnaire_id = questionnaire_id;
		this.registerWithDispatcher();
		this.questions = [];
	}

	getAllQuestions() {
		return this.questions;
	}

	addChangeListener(callback) {
		this.on(CHANGE_EVENT,callback);
	}

	removeChangeListener(callback){
		this.removeListener(CHANGE_EVENT, callback);
	}

	emitChange() {
		this.emit(CHANGE_EVENT)
	}

	dispatchHandler(action) {
		switch(action.type){
			case AppConstants.ActionTypes.INITIALIZE_QUESTIONNAIRE:
				debugger;
			      this.questions = action.questions;
			      this.emitChange();
			      break;
			 default:
				 //pass

		}

	}

	registerWithDispatcher(){
		AppDispatcher.register(this.dispatchHandler);

	}

}
module.exports = new QuestionnaireStore();
*/

module.exports = QuestionnaireStore;
