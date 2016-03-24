import React from 'react';
import QuestionnaireStore from '../store/questionnaire-store';

let getAllQuestions = function(questionnaire_id){
	return {
		questions: QuestionnaireStore.getAllQuestions(questionnaire_id)
	};
};

export default class QuestionnaireList extends React.Component {
	constructor(props){
		super(props);
		this.state = {
				questionnaire_id:props.questionnaire_id,
				questions: getAllQuestions(props.questionnaire_id)
		}
	}
		
	componentWillMount(){
		QuestionnaireStore.addChangeListener(this._onChange);
	}
	
	_onChange(){
		this.setState({questions:getAllQuestions(this.state.id)})
	}
	
	render(){

		return (
				<div>
				<h1>Inside questionnaire list for Question ID : {this.state.questionnaire_id}</h1>
				</div>
				);
	}
}