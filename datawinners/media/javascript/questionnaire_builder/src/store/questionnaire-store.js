import {EventEmitter} from 'events';

const CHANGE_EVENT = 'change';
import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';

var QuestionnaireStore = Object.assign({},EventEmitter.prototype, {
	questionnaire: {},

	addChangeListener: function (callback) {
		this.on(CHANGE_EVENT,callback);
	},

	removeChangeListener: function (callback) {
		this.removeListener(CHANGE_EVENT, callback);
	},

	emitChange: function () {
		this.emit(CHANGE_EVENT)
	},

	getQuestionnaire: function () {
		// TO DO: to be removed. we can use either this or QuestionnaireStore.questionnaire
		return this.questionnaire;
	},

	questionFields: function () {
		return Object.keys(this.questionnaire.survey[0]);
	},

	findQuestionIndex: function (question) {
		let index = _.findIndex(this.questionnaire.survey, {temp_id: question.temp_id});
	  if(index < 0){
	    index = _.findIndex(this.questionnaire.survey, {name: question.name});
	  }
	  return index;
	},

	load: function (questionnaire) {
		this.questionnaire = questionnaire;
	},

	add: function (question) {
		this.questionnaire.survey.push(question);
	},

	update: function (question) {
		this.questionnaire.survey[this.findQuestionIndex(question)] = question;
	},

	delete: function (question) {
		this.questionnaire.survey.splice(this.findQuestionIndex(question), 1);
	}

});

AppDispatcher.register(function (action) {
		//TODO: this needs to be updated
	switch (action.actionType) {
		case AppConstants.ActionTypes.UPDATE_QUESTION:
		case AppConstants.ActionTypes.CREATE_QUESTION:
		case AppConstants.ActionTypes.DELETE_QUESTION:
			QuestionnaireStore.emitChange();
			break;
		default:
			//do nothing
	}
});

module.exports = QuestionnaireStore;
