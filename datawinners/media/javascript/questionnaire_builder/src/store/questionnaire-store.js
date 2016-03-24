import {EventEmitter} from 'events';

const CHANGE_EVENT = 'change';
import SampleQuestionnaire from './sample-questionnaire';

var QuestionnaireStore = Object.assign({},EventEmitter.prototype, {
//	constructor(questionnaire_id){
//		super();
//		this.questionnaire_id = questionnaire_id;
//	}
	
	getAllQuestions: function() {
		console.log(SampleQuestionnaire.questions);
		return SampleQuestionnaire.questions;
	},
	
	addChangeListener: function(callback) {
		this.on(CHANGE_EVENT,callback);
	},
	
	removeChangeListener:function(callback){
		this.removeListener(CHANGE_EVENT, callback);
	},
	
	emitChange: function(){
		this.emit(CHANGE_EVENT)
	}
	
});

module.exports = QuestionnaireStore;