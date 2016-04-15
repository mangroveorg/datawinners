
import React from 'react';
import QuestionnaireStore from '../store/questionnaire-store';
import AppConstants from '../constants/app-constants';
import Question from './question';
import Paper from 'material-ui/lib/paper';

import IconButton from 'material-ui/lib/icon-button';
import FloatingActionButton from 'material-ui/lib/floating-action-button';
import ContentAdd from 'material-ui/lib/svg-icons/content/add';
import Card from 'material-ui/lib/card/card';
import CardText from 'material-ui/lib/card/card-text';
import QuestionnaireActions from '../actions/questionnaire-actions';
import LinearProgress from 'material-ui/lib/linear-progress';
import BuilderToolbar from './builder-toolbar';
import Tabs from 'material-ui/lib/tabs/tabs';
import Tab from 'material-ui/lib/tabs/tab';
import FontIcon from 'material-ui/lib/font-icon';
import FormFactory from './form-factory';
import ChoiceGroup from './choice-group';

const style = {
	addButtonContainer: {
		position: 'relative',
    bottom: '22px',
    right: '20px',
    float: 'right'
	},
	saveButton: {
		backgroundColor: 'red'
	},
	tabs: {
		backgroundColor: '#329CDC'
	},
	headline: {
	    fontSize: 24,
	    paddingTop: 16,
	    marginBottom: 12,
	    fontWeight: 400,
	  },
  slide: {
    padding: 10
  },
};

//TODO: could move this transform to QuestionnaireStore
var transformChoices = function(choices){
	let choicesWithoutEmpty = _.filter(
																	choices,
																	function(c){
																		return !_.isEmpty(_.trim(c['list name']));
																	});
	let choicesGrouped = _.groupBy(choicesWithoutEmpty,'list name');
	return choicesGrouped;
};

export default class QuestionnaireList extends React.Component {
	constructor(props){
		super(props);
		this.state = {
				questionnaire_id:props.questionnaire_id,
			 	slideIndex: 0

		}
		this.onChange = this.onChange.bind(this);
		this.onDelete = this.onDelete.bind(this);
		this.saveQuestionnaire = this.saveQuestionnaire.bind(this);
		this.handleAddButtonClick = this.handleAddButtonClick.bind(this);
		this.handleChoiceAddButtonClick = this.handleChoiceAddButtonClick.bind(this);
		this._onChange = this._onChange.bind(this);
	}

	componentDidMount(){
		let url = AppConstants.QuestionnaireUrl + this.state.questionnaire_id + '/';
		var self = this;
		this.serverRequest = $.ajax({
				url: url,
				dataType: 'json',
				success: function (result) {
					QuestionnaireStore.load(result.questionnaire);

		      self.setState({
		        questionnaire: result.questionnaire,
						file_type: result.file_type,
						reason: result.reason,
						details: result.details
		      });

				}
			});
	}

	componentWillMount(){
		QuestionnaireStore.addChangeListener(this._onChange);
	}

	componentWillUnmount() {
		this.serverRequest.abort();
	}

	handleAddButtonClick() {
		QuestionnaireActions.createQuestion();
  }

	handleChoiceAddButtonClick(){
		QuestionnaireActions.createChoice(this.state.questionnaire);
	}

	_onChange(){
		this.setState({questionnaire:QuestionnaireStore.getQuestionnaire()});
	}

	saveQuestionnaire(event) {
		event.preventDefault();

		let status = QuestionnaireActions.saveQuestionnaire(
											this.state.questionnaire_id,this.state.questionnaire, this.state.file_type);
	}

	onChange(question) {
		QuestionnaireActions.updateQuestion(question);
	}

	onDelete(question) {
		QuestionnaireActions.deleteQuestion(question);
	}

	getListOfQuestionViews(){
		var questions = this.state.questionnaire.survey;
    var questionViews = [];

    for (var key in questions) {
			if (FormFactory.getFormForQuestionType(questions[key].type)) {
				questionViews.push(
					<Question
							question={questions[key]}
							onChange={this.onChange}
							onDelete={this.onDelete}
							/>
				);
			}
    }
		return questionViews;

	}

	getListOfChoiceGroupViews(){
		let choices = this.state.questionnaire.choices;
		let choicesGrouped = transformChoices(choices);
		let choiceGroupViews = [];
		for (var key in choicesGrouped){
			choiceGroupViews.push(
				<ChoiceGroup
						choiceGroup={choicesGrouped[key]}
						onChoiceRowSelection={this.onChoiceRowSelection}
						/>
			)
		}
		return choiceGroupViews;
	}

	render(){

		if (!this.state.questionnaire){
			return (
				<div>
					<LinearProgress mode="indeterminate" />
					<h4>{this.state.reason}</h4>
					<h5>{this.state.details}</h5>
				</div>
			)
		}

		return (
			<div>
      <Paper zDepth={3} >
				<BuilderToolbar onSave={this.saveQuestionnaire}/>
					<Tabs tabItemContainerStyle={style.tabs}>
				    <Tab
				      icon={<FontIcon className="material-icons">assignment</FontIcon>}
				      label="Survey" value={0}
				    >
							{this.getListOfQuestionViews()}
							<div style={style.addButtonContainer}>
		            <FloatingActionButton onMouseDown={this.handleAddButtonClick}>
		              <ContentAdd />
		            </FloatingActionButton>
		          </div>
						</Tab>
				    <Tab
				      icon={<FontIcon className="material-icons">assignment_turned_in</FontIcon>}
				      label="Choices" value={1}
				    >
							{this.getListOfChoiceGroupViews()}
							<div style={style.addButtonContainer}>
		            <FloatingActionButton onMouseDown={this.handleChoiceAddButtonClick}>
		              <ContentAdd />
		            </FloatingActionButton>
		          </div>
						</Tab>
				    <Tab
				      icon={<FontIcon className="material-icons">low_priority</FontIcon>}
				      label="Cascades" value={2}
				    >
							<h3>Cascades gets listed here</h3>
						</Tab>
				  </Tabs>

      </Paper>
      </div>
				);
	}
}
