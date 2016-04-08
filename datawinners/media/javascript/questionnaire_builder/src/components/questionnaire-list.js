import React from 'react';
import QuestionnaireStore from '../store/questionnaire-store';
import AppConstants from '../constants/app-constants';
import Question from './question';
import Paper from 'material-ui/lib/paper';
import AppBar from 'material-ui/lib/app-bar';

import IconButton from 'material-ui/lib/icon-button';
import RaisedButton from 'material-ui/lib/raised-button';
import FloatingActionButton from 'material-ui/lib/floating-action-button';
import ContentAdd from 'material-ui/lib/svg-icons/content/add';
import Card from 'material-ui/lib/card/card';
import CardText from 'material-ui/lib/card/card-text';
import SelectField from 'material-ui/lib/select-field';
import QuestionnaireActions from '../actions/questionnaire-actions';
import MenuItem from 'material-ui/lib/menus/menu-item';
import _ from 'lodash';
import LinearProgress from 'material-ui/lib/linear-progress';
import BuilderToolbar from './builder-toolbar';
import Tabs from 'material-ui/lib/tabs/tabs';
import Tab from 'material-ui/lib/tabs/tab';
import FontIcon from 'material-ui/lib/font-icon';
import SwipeableViews from 'react-swipeable-views';

const style = {
	addButtonContainer: {
		position: 'relative',
    bottom: '22px',
    right: '20px',
    float: 'right'
	},
	appBar: {
		backgroundColor: '#E8EFF6'
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
//
// let getAllQuestions = function(questionnaire_id){
// 	return {
// 		questions: QuestionnaireStore.getAllQuestions(questionnaire_id)
// 	};
// };

export default class QuestionnaireList extends React.Component {
	constructor(props){
		super(props);
		this.state = {
				questionnaire_id:props.questionnaire_id,
			 	slideIndex: 0
		}
		this.onQuestionChange = this.onQuestionChange.bind(this);
		this.saveQuestionnaire = this.saveQuestionnaire.bind(this);
		this.handleChange = this.handleChange.bind(this);
	}

	componentDidMount(){
		let url = AppConstants.QuestionnaireUrl + this.state.questionnaire_id + '/';
		var self = this;
		this.serverRequest = $.ajax({
				url: url,
				dataType: 'json',
				success: function (result) {
		      self.setState({
		        questionnaire: result.questionnaire,
						file_type: result.file_type
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

	_onChange(){
		this.setState({questions:getAllQuestions(this.state.id)})
	}

	onQuestionChange(updated_question){
		let current_question_index = _.findIndex(
																					this.state.questionnaire.survey,
																					{name:updated_question.name});
		let questions = this.state.questionnaire.survey;
		questions[current_question_index] = updated_question;
		this.setState({questions: questions});
	}

	getQuestionTypeMenuItems() {
    var question_type_menu_items = [];
    for (var key in AppConstants.QuestionTypesDropdown){
      question_type_menu_items.push(
        <MenuItem
						value={AppConstants.QuestionTypesDropdown[key]}
						primaryText={AppConstants.QuestionTypesDropdown[key]} />
      );
    }
    return question_type_menu_items;
  }

	saveQuestionnaire(event) {
		event.preventDefault();

		let status = QuestionnaireActions.saveQuestionnaire(
											this.state.questionnaire_id,this.state.questionnaire, this.state.file_type);
	}

	handleChange(value) {
    this.setState({
      slideIndex: value,
    });
  };

	render(){
		if (!this.state.questionnaire){
			return (
				<div>
					<LinearProgress mode="indeterminate" />
					</div>
			)
		}
		var questions = this.state.questionnaire.survey;
    var displayQuestions = [];

    for (var key in questions) {
			if (AppConstants.QuestionTypeSupport[questions[key].type]) {
				displayQuestions.push(
					<Question
							key={questions[key].name}
							question={questions[key]}
							onChange={this.onQuestionChange}/>
				);
			}
    }

		return (
			<div>
      <Paper zDepth={3} >
				<BuilderToolbar onSave={this.saveQuestionnaire}/>
					<Tabs onChange={this.handleChange}
          			value={this.state.slideIndex} tabItemContainerStyle={style.tabs}>
				    <Tab
				      icon={<FontIcon className="material-icons">phone</FontIcon>}
				      label="Survey" value={0}
				    >

						</Tab>
				    <Tab
				      icon={<FontIcon className="material-icons">favorite</FontIcon>}
				      label="Choices" value={1}
				    />
				    <Tab
				      icon={<FontIcon className="material-icons">person_pin</FontIcon>}
				      label="Cascades" value={2}
				    />
				  </Tabs>
					<SwipeableViews
	          index={this.state.slideIndex}
	          onChangeIndex={this.handleChange}
	        >
	          <div style={style.slide}>
							{displayQuestions}
	          </div>
	          <div style={style.slide}>
	            slide n°2
	          </div>
	          <div style={style.slide}>
	            slide n°3
	          </div>
	        </SwipeableViews>

          <Card expanded={this.state.expandNewQuestionType}>
          <CardText expandable={true}>
                <SelectField
                          floatingLabelText="Question Type"
                        >
                          {this.getQuestionTypeMenuItems()}
                  </SelectField>
            </CardText>
          </Card>
          <div style={style.addButtonContainer}>
            <FloatingActionButton onMouseDown={this.handleAddButtonClick}>
              <ContentAdd />
            </FloatingActionButton>
          </div>
      </Paper>
      </div>
				);
	}
}
