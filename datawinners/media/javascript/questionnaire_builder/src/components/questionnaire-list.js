import React from 'react';
import QuestionnaireStore from '../store/questionnaire-store';
import AppConstants from '../constants/app-constants';
import Question from './question';
import Paper from 'material-ui/lib/paper';
import AppBar from 'material-ui/lib/app-bar';

import IconButton from 'material-ui/lib/icon-button';
import ActionHome from 'material-ui/lib/svg-icons/action/home';
import RaisedButton from 'material-ui/lib/raised-button';
import FloatingActionButton from 'material-ui/lib/floating-action-button';
import ContentAdd from 'material-ui/lib/svg-icons/content/add';
import Card from 'material-ui/lib/card/card';

// var CardActions = require('material-ui/lib/card/card-actions');
import CardText from 'material-ui/lib/card/card-text';
import SelectField from 'material-ui/lib/select-field';

import MenuItem from 'material-ui/lib/menus/menu-item';
import _ from 'lodash';

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
	}
};

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
		this.onQuestionChange = this.onQuestionChange.bind(this);
	}

	componentDidMount(){
		let url = AppConstants.QuestionnaireUrl + this.state.questionnaire_id;
		var self = this;
		this.serverRequest = $.ajax({
				url: url,
				success: function (result) {
		      var lastGist = result.questions;
		      self.setState({
		        questions: result.questions,
						name: result.name
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
																					this.state.questions,
																					{name:updated_question.name});
		let questions = this.state.questions;
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

	render(){
		var questions = this.state.questions;
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
        <AppBar
					showMenuIconButton={false}
          title={<span>Questionnaire Builder</span>}
          iconElementRight={<RaisedButton label="Save" style={style.saveButton} />}
          />
					{displayQuestions}

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
