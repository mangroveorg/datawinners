import {EventEmitter} from 'events';

const CHANGE_EVENT = 'change';
import AppDispatcher from '../dispatcher/app-dispatcher';
import AppConstants from '../constants/app-constants';
import Validator from './validator';
import _ from 'lodash';

var _questionnaireId = undefined;
var _fileType = undefined;
var _questionnaire = {};
var _errors = [];
var _uniqueIdTypes = [];
var _choicesGrouped = {};
var _cascadesGrouped = [];
var _initErrors = {};

var createChoiceGroup = () => {
	let choice = _defaultChoice();
	choice.isNewChoiceGroup = true;
	if (!_questionnaire.choices) {
		_questionnaire.choices = [];
	}
	_questionnaire.choices.push(choice);
	computeChoicesGrouped();
};

var createChoice = (data) => {
	let choice = _defaultChoice();
	choice[data.added_field]=data.value;
	choice['list_name'] = data.choiceGroupName;
	if (!_questionnaire.choices) {
		_questionnaire.choices = [];
	}
	_questionnaire.choices.push(choice);
	computeChoicesGrouped();
};

var _defaultChoice = () => {
	let choice = {};
	let choiceFields = QuestionnaireStore.choiceFields();
	for (let required_field of choiceFields){
		choice[required_field] = '';
	}
	return choice;
}

var	updateSaveError = (errors) => {
		_errors = errors;
}

var removeQuestionValidationErrorsIfExists = function (question) {
	_.remove(_errors, function (error) {
			let errorKey = question.temp_id || question.name;
			return error[errorKey];
		});
};

var removeChoiceValidationErrorsIfExists = function (choice) {
	_.remove(_errors, function (error) {
		return error[choice.base_index];
	});
};

var removeEmptyRowsFromSurvey = () => {
	_questionnaire.survey = _.filter(_questionnaire.survey, function(q){
		return !_.isEmpty(_.trim(q.type));
	});
}

var flagSupportedQuestionTypes = () => {
	_questionnaire.survey = _.forEach(_questionnaire.survey, function(q){
		let questionType = _.split(q.type,' ');
		q.isSupported = _.find(AppConstants.QuestionTypes, {value: questionType[0]}) ? true : false;
		return q;
	});
}

var renameChoiceListName = () => {
	_questionnaire.choices = _.forEach(_questionnaire.choices, function(c){
		if ('list name' in c) {
			c.list_name = c['list name'];
			delete c['list name'];
			delete c[''];//cleanup
			delete c[-1];//cleanup
			return c;
		}
	});
}

var removeEmptyRowsFromChoices = () => {
	_questionnaire.choices = _.filter(
																	_questionnaire.choices,
																	function(c){
																		return !_.isEmpty(_.trim(c['list_name']));
																	});

}

var computeChoicesGrouped = () => {
	if (!_questionnaire.choices){
		_choicesGrouped = {};
		return ;
	}
	for (var index in _questionnaire.choices){
		_questionnaire.choices[index]['base_index'] = index;
	}
	_choicesGrouped = _.groupBy(_questionnaire.choices,'list_name');

}

var computeCascadesGrouped = () => {
	if (!_questionnaire.cascades){
		_cascadesGrouped = [];
		return ;
	}
	for (let index in _questionnaire.cascades){
		_questionnaire.cascades[index]['base_index']=index;
	}
	let cascadesWithoutEmpty = _.filter(
																	_questionnaire.cascades,
																	function(c){
																		return !_.isEmpty(_.trim(c['name']));
																	});
	let cascadesHeader = _questionnaire.cascades[0];
	let cascadesWithoutHeader = _.slice(_questionnaire.cascades,1);
	let cascadesHeaderKeys = _.without(_.keys(cascadesHeader),'name','base_index');
	_cascadesGrouped = [];
	for (let key of cascadesHeaderKeys){
		_cascadesGrouped.push({
			name: key,
			label: cascadesHeader[key]
		});
	}
}
var findQuestionIndex = function (question) {
		let index = _.findIndex(_questionnaire.survey, {temp_id: question.temp_id});
	  if(index < 0){
	    index = _.findIndex(_questionnaire.survey, {name: question.name});
	  }
	  return index;
}

var moveUp = function (question) {
	let index = findQuestionIndex(question);
	if(index > 0) {
		let previousIndex = index - 1;
		var previousQuestion = _questionnaire.survey[previousIndex];
		console.log(AppConstants.GroupBoundaries);
		if (AppConstants.GroupBoundaries.indexOf(previousQuestion.type) == -1) {
			_questionnaire.survey[index] = previousQuestion;
			_questionnaire.survey[previousIndex] = question;
		}
	}
}

var moveDown = function (question) {
	let index = findQuestionIndex(question);
	if(index < _questionnaire.survey.length - 1) {
		let nextIndex = index + 1;
		let nextQuestion = _questionnaire.survey[nextIndex];
		if (AppConstants.GroupBoundaries.indexOf(nextQuestion.type) == -1) {
			_questionnaire.survey[index] = nextQuestion;
			_questionnaire.survey[nextIndex] = question;
		}
	}
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

	getQuestionnaireId: function () {
		return _questionnaireId;
	},

	getFileType: function () {
		return _fileType;
	},

	getQuestionnaire: function () {
		return _questionnaire;
	},

	getUniqueIdTypes: function () {
		return _uniqueIdTypes;
	},

	getChoicesGrouped: function() {
		return _choicesGrouped;
	},

	getCascadesGrouped: function(){
		return _cascadesGrouped;
	},

	getErrors: function(){
		return _errors;
	},

	getInitErrors: function(){
		return _initErrors;
	},

	errorsPresent: function () {
		_errors = [];
		_errors = _.concat(_errors, Validator.validateQuestionnaire(_questionnaire));
		_errors = _.concat(_errors, Validator.validateChoices(_questionnaire));
		QuestionnaireStore.emitChange();
		return _errors.length > 0;
	},

	questionFields: function () {
		return Object.keys(_questionnaire.survey[0]);
	},

	choiceFields: function() {
			if (_questionnaire.choices && _questionnaire.choices[0]){
				return Object.keys(_questionnaire.choices[0]);
			} else {
				return ['list_name','name','label'];
			}
	},

	findChoiceIndex: function(choice){
		return _.findIndex(_questionnaire.choices, {base_index: choice.base_index});
	},

	loadUniqueIdTypes: function (uniqueIdTypes) {
		_uniqueIdTypes = uniqueIdTypes || [];
	},

	loadQuestionnaireId: function (questionnaireId) {
		_questionnaireId = questionnaireId;
	},

	loadFileType: function (fileType) {
		_fileType = fileType;
	},

	loadInitErrors: function(reason, details){
		_initErrors.reason = reason;
		_initErrors.details = details;
	},

	loadQuestionnaire: function (questionnaire) {
		// injectTempId(questionnaire.survey);
		if (!questionnaire.choices) {
			questionnaire.choices = [];
		}
		_questionnaire = questionnaire;
		removeEmptyRowsFromSurvey();
		renameChoiceListName();
		removeEmptyRowsFromChoices();
		flagSupportedQuestionTypes();
		computeChoicesGrouped();
		// computeCascadesGrouped();
	},

	add: function (question) {
		_questionnaire.survey.push(question);
	},

	update: function (question) {
		_questionnaire.survey[findQuestionIndex(question)] = question;
		removeQuestionValidationErrorsIfExists(question);
		_errors = _.concat(_errors, Validator.validateQuestion(question));
	},

	delete: function (question) {
		_questionnaire.survey.splice(findQuestionIndex(question), 1);
	},

	updateChoice: function(choice) {
		removeChoiceValidationErrorsIfExists(choice);
		_errors = _.concat(_errors, Validator.validateChoice(choice));
		_questionnaire.choices[this.findChoiceIndex(choice)] = choice;
		computeChoicesGrouped();
	},

	deleteChoice: function(base_index){
		_questionnaire.choices.splice(base_index, 1);
		computeChoicesGrouped();
	}

});

AppDispatcher.register(function (action) {
		//TODO: this needs to be updated. Emit change can go inside each method instead of duplicate call?
	switch (action.actionType) {
		case AppConstants.ActionTypes.INITIALIZE_QUESTIONNAIRE:
		case AppConstants.ActionTypes.UPDATE_QUESTION:
		case AppConstants.ActionTypes.CREATE_QUESTION:
		case AppConstants.ActionTypes.DELETE_QUESTION:
		case AppConstants.ActionTypes.UPDATE_CHOICE:
		case AppConstants.ActionTypes.DELETE_CHOICE:
			QuestionnaireStore.emitChange();
			break;
		case AppConstants.ActionTypes.MOVE_UP:
			moveUp(action.data.question);
			QuestionnaireStore.emitChange();
			break;
		case AppConstants.ActionTypes.MOVE_DOWN:
			moveDown(action.data.question);
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
		case AppConstants.ActionTypes.ERROR_ON_SAVE:
			updateSaveError(action.data);
			QuestionnaireStore.emitChange();
			break;
		default:
			//do nothing
	}
});

module.exports = QuestionnaireStore;
