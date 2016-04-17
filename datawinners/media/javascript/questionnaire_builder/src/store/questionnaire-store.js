import {EventEmitter} from 'events';

const CHANGE_EVENT = 'change';
import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';
import _ from 'lodash';

var questionnaire = {};

var QuestionnaireStore = Object.assign({},EventEmitter.prototype, {

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
		return this.questionnaire;
	},

	getChoicesGrouped: function() {
		for (var index in this.questionnaire.choices){
			this.questionnaire.choices[index]['base_index'] = index;
		}
		let choicesWithoutEmpty = _.filter(
																		this.questionnaire.choices,
																		function(c){
																			return !_.isEmpty(_.trim(c['list name']));
																		});
		let choicesGrouped = _.groupBy(choicesWithoutEmpty,'list name');

		return choicesGrouped;
	},

	questionFields: function () {
		return Object.keys(this.questionnaire.survey[0]);
	},

	choiceFields: function() {
		if (this.questionnaire.choices && this.questionnaire.choices[0]){
			return Object.keys(this.questionnaire.choices[0]);
		}else{
			return {
				'list name':'',
				'name':'',
				'label':''
			};
		}
	},

	findQuestionIndex: function (question) {
		let index = _.findIndex(this.questionnaire.survey, {temp_id: question.temp_id});
	  if(index < 0){
	    index = _.findIndex(this.questionnaire.survey, {name: question.name});
	  }
	  return index;
	},

	findChoiceIndex: function(choice){
		return _.findIndex(this.questionnaire.choices, {base_index: choice.base_index});
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
	},

	updateChoice: function(choice) {
		this.questionnaire.choices[this.findChoiceIndex(choice)] = choice;
	},

	deleteChoice: function(base_index){
		this.questionnaire.choices.splice(base_index, 1);
	},

	createChoice: function(choice){
		this.questionnaire.choices.push(choice);
	}

});

AppDispatcher.register(function (action) {
		//TODO: this needs to be updated
	switch (action.actionType) {
		case AppConstants.ActionTypes.UPDATE_QUESTION:
		case AppConstants.ActionTypes.CREATE_QUESTION:
		case AppConstants.ActionTypes.DELETE_QUESTION:
		case AppConstants.ActionTypes.CREATE_CHOICE:
		case AppConstants.ActionTypes.UPDATE_CHOICE:
		case AppConstants.ActionTypes.DELETE_CHOICE:
			QuestionnaireStore.emitChange();
			break;
		default:
			//do nothing
	}
});

module.exports = QuestionnaireStore;
