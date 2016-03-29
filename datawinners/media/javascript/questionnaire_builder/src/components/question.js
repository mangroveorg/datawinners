import React from 'react';
import QuestionActions from '../actions/questionnaire-actions';
import Toastr from 'toastr';
import Card from 'material-ui/lib/card/card';
import CardHeader from 'material-ui/lib/card/card-header';
import CardText from 'material-ui/lib/card/card-text';
import AppConstants from '../constants/app-constants';
import TextQuestionForm from './text-question-form';

const style = {
  question_row: {
    background: "azure",
    borderBottomStyle: "solid",
    borderBottomColor: "grey",
    borderWidth: "2px"
  }
}

export default class Question extends React.Component {
  constructor(props){
    super(props);
    let question = {
      id: '',
      label: '',
      name: '',
      type: 'text',
      hint:'',
      required: ''

    };
    this.errors = {};
    if(this.props.question){
      question = this.props.question;
    }

    this.formType = AppConstants.QuestionTypeSupport[question.type];
    this.setQuestionState = this.setQuestionState.bind(this);
  }

  setQuestionState(event) {
		let field = event.target.name;
		let value = event.target.value;
    let question = this.props.question;
    question[field] = value;
    question.dirty = true;
    this.props.onChange(question);
	}

  questionFormIsValid() {
    return true;//TODO
  }

  saveQuestion(event) {
		event.preventDefault();

		if (!this.questionFormIsValid()) {
			return;
		}

    //TODO - id is not longer meaningful.,
		if (this.state.question.id) {
			QuestionActions.updateQuestion(this.state.question);
		} else {
			QuestionActions.createQuestion(this.state.question);
		}

		// this.setState({dirty: false});
		Toastr.success('Question saved.');
	}

  render() {
      var name = this.props.question.name;
      return (
        <Card>
          <CardHeader
            title={this.props.question.label}
            subtitle={this.props.question.type}
            actAsExpander={true}
            showExpandableButton={true}
            style={style.question_row}
          />
          <CardText expandable={true}>
              <TextQuestionForm
                question={this.props.question}
                onChange={this.setQuestionState}
                onSave={this.saveQuestion}
                errors={this.errors} />

          </CardText>
        </Card>

      );
  }


}
