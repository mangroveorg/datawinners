import {EventEmitter} from 'events';

const CHANGE_EVENT = 'change';
import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';
import _ from 'lodash';

var _questionnaire = {};

var createChoiceGroup = () => {
	let choice = _defaultChoice();
	choice.isNewChoiceGroup = true;
	_questionnaire.choices.push(choice);
};

var createChoice = (data) => {
	let choice = _defaultChoice();
	choice[data.added_field]=data.value;
	choice['list name'] = data.choiceGroupName;
	_questionnaire.choices.push(choice);
};

var _defaultChoice = () => {
	let choice = {};
	let choiceFields = QuestionnaireStore.choiceFields();
	for (let required_field of choiceFields){
		choice[required_field] = '';
	}
	return choice;
}

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
		return _questionnaire;
	},

	getChoicesGrouped: function() {
		//TODO: Need not be computed everytime. Only on change of choices, this will change
		for (var index in _questionnaire.choices){
			_questionnaire.choices[index]['base_index'] = index;
		}
		let choicesWithoutEmpty = _.filter(
																		_questionnaire.choices,
																		function(c){
																			return c.isNewChoiceGroup || !_.isEmpty(_.trim(c['list name']));
																		});
		let choicesGrouped = _.groupBy(choicesWithoutEmpty,'list name');

		return choicesGrouped;
	},

	questionFields: function () {
		return Object.keys(_questionnaire.survey[0]);
	},

	choiceFields: function() {
			if (_questionnaire.choices && _questionnaire.choices[0]){
				return Object.keys(_questionnaire.choices[0]);
			}else{
				return ['list name','name','label'];
			}
	},

	findQuestionIndex: function (question) {
		let index = _.findIndex(_questionnaire.survey, {temp_id: question.temp_id});
	  if(index < 0){
	    index = _.findIndex(_questionnaire.survey, {name: question.name});
	  }
	  return index;
	},

	findChoiceIndex: function(choice){
		return _.findIndex(_questionnaire.choices, {base_index: choice.base_index});
	},

	load: function (questionnaire) {
		_questionnaire = questionnaire;
		if (!_questionnaire.choices){
			_questionnaire.choices = [];//Initialize choices
		}
	},

	add: function (question) {
		_questionnaire.survey.push(question);
	},

	update: function (question) {
		_questionnaire.survey[this.findQuestionIndex(question)] = question;
	},

	delete: function (question) {
		_questionnaire.survey.splice(this.findQuestionIndex(question), 1);
	},

	updateChoice: function(choice) {
		_questionnaire.choices[this.findChoiceIndex(choice)] = choice;
	},

	deleteChoice: function(base_index){
		_questionnaire.choices.splice(base_index, 1);
	},

	createChoice: function(choice){
		_questionnaire.choices.push(choice);
	}

});

AppDispatcher.register(function (action) {
		//TODO: this needs to be updated
	switch (action.actionType) {
		case AppConstants.ActionTypes.UPDATE_QUESTION:
		case AppConstants.ActionTypes.CREATE_QUESTION:
		case AppConstants.ActionTypes.DELETE_QUESTION:
		case AppConstants.ActionTypes.UPDATE_CHOICE:
		case AppConstants.ActionTypes.DELETE_CHOICE:
			QuestionnaireStore.emitChange();
			break;
		case AppConstants.ActionTypes.CREATE_CHOICE_GROUP:
			createChoiceGroup();
			QuestionnaireStore.emitChange();
			break;
		case AppConstants.ActionTypes.CREATE_CHOICE:
			createChoice(action.data);
			QuestionnaireStore.emitChange();
			break;
		default:
			//do nothing
	}
});

module.exports = QuestionnaireStore;
