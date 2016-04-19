
import React from 'react';
import QuestionnaireStore from '../store/questionnaire-store';
import AppConstants from '../constants/app-constants';
import Paper from 'material-ui/Paper';

import IconButton from 'material-ui/IconButton';
import FloatingActionButton from 'material-ui/FloatingActionButton';
import ContentAdd from 'material-ui/svg-icons/content/add';
import Card from 'material-ui/Card/Card';
import CardText from 'material-ui/Card/CardText';
import QuestionnaireActions from '../actions/questionnaire-actions';
import LinearProgress from 'material-ui/LinearProgress';
import BuilderToolbar from './builder-toolbar';
import Tabs from 'material-ui/Tabs/Tabs';
import Tab from 'material-ui/Tabs/Tab';
import FontIcon from 'material-ui/FontIcon';
import FormFactory from './form-factory';
import ChoicesTab from './choices-tab';
import SurveyTab from './survey-tab';
import _ from 'lodash';

const style = {
	tabs: {
		backgroundColor: '#329CDC'
	}
};

export default class QuestionnaireList extends React.Component {
	constructor(props){
		super(props);
		this.state = {
				questionnaire_id:props.questionnaire_id,
			 	currentTab: 'survey',
				errors:[]

		}
		this._onChange = this._onChange.bind(this);
	}

	componentDidMount(){
		//TODO: this should happen through action
		let url = AppConstants.QuestionnaireUrl + this.state.questionnaire_id + '/';
		var self = this;
		this.serverRequest = $.ajax({
				url: url,
				data: {reload:reload},
				dataType: 'json',
				success: function (result) {
					QuestionnaireStore.load(result.questionnaire);

		      self.setState({
		        questionnaire: result.questionnaire,
						choicesGrouped: QuestionnaireStore.getChoicesGrouped(),
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

	onTabChange = (value) => {
		let validTabs = ['survey','choices','cascades'];
		if (_.includes(validTabs, value)){
			this.setState({currentTab: value});
		}
	}

	_onChange(){
		this.setState({
			questionnaire:QuestionnaireStore.getQuestionnaire(),
			choicesGrouped:QuestionnaireStore.getChoicesGrouped(),
			errors:QuestionnaireStore.getErrors()
		});
	}

	saveQuestionnaire = (event) => {
		event.preventDefault();
		//TODO - should take questionnaire from store, not from here
		let status = QuestionnaireActions.saveQuestionnaire(
											this.state.questionnaire_id,this.state.questionnaire, this.state.file_type);
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
				<BuilderToolbar key='builder_toolbar' onSave={this.saveQuestionnaire}/>
					<Tabs tabItemContainerStyle={style.tabs}
								value={this.state.currentTab}
        				onChange={this.onTabChange}>
				    <Tab
				      icon={<FontIcon className="material-icons">assignment</FontIcon>}
				      label="Survey" value='survey'
							key='survey'
				    >
							<SurveyTab currentTab={this.state.currentTab}
												survey={this.state.questionnaire.survey}
												errors={this.state.errors}/>
						</Tab>
				    <Tab
				      icon={<FontIcon className="material-icons">assignment_turned_in</FontIcon>}
				      label="Choices" value='choices'
							key='choices'
				    >
							<ChoicesTab currentTab={this.state.currentTab}
													choicesGrouped={this.state.choicesGrouped}
													errors={this.state.errors}/>
						</Tab>
				    <Tab
				      icon={<FontIcon className="material-icons">low_priority</FontIcon>}
				      label="Cascades" value='cascades'
							key='cascades'
				    >
							<h3>Cascades gets listed here</h3>
						</Tab>
				  </Tabs>

      </Paper>
      </div>
				);
	}
}
