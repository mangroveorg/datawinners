import React from 'react';
import QuestionnaireActions from '../actions/questionnaire-actions';
// import QuestionnaireStore from '../store/questionnaire-store';
import ChoiceGroup from './choice-group';
import FloatingActionButton from 'material-ui/FloatingActionButton';
import ContentAdd from 'material-ui/svg-icons/content/add';
import Question from './question';
import FormFactory from './form-factory';

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
};

export default class SurveyTab extends React.Component {
  constructor(props){
    super(props);
  }

  onChange = (question) => {
		QuestionnaireActions.updateQuestion(question);
	}

	onDelete = (question) => {
		QuestionnaireActions.deleteQuestion(question);
	}

  handleAddButtonClick = () => {
		QuestionnaireActions.createQuestion();
  }


  getListOfQuestionViews(){
		var questions = this.props.survey;
    var questionViews = [];

    for (var key in questions) {
			if (FormFactory.getFormForQuestionType(questions[key].type)) {
				let errors = {};
				if (this.props.errors && this.props.errors[questions[key].name]){
					errors = this.props.errors[questions[key].name];
				}
				questionViews.push(
					<Question
							key={'question_'+key}
							question={questions[key]}
							onChange={this.onChange}
							onDelete={this.onDelete}
							errors={errors}
							/>
				);
			}
    }
		return questionViews;

	}

  render() {
    if (this.props.currentTab == 'survey') {
      return (
        <div>
          {this.getListOfQuestionViews()}
          <div style={style.addButtonContainer}>
            <FloatingActionButton onMouseDown={this.handleAddButtonClick}>
              <ContentAdd />
            </FloatingActionButton>
          </div>
        </div>
      );
    } else {
      return (
          <div>This page will be loaded on survey tab</div>
        ); //To optimize performance and minimize DOM content
    }


  }
}