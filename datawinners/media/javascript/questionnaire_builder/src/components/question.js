import React from 'react';
import QuestionActions from '../actions/questionnaire-actions';
import Toastr from 'toastr';
import Card from 'material-ui/lib/card/card';
import CardHeader from 'material-ui/lib/card/card-header';
import CardText from 'material-ui/lib/card/card-text';
import AppConstants from '../constants/app-constants';
import TextQuestionForm from './textQuestionForm';

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
    if(this.props.question){
      question = this.props.question;
    }

    this.formType = AppConstants.QuestionTypeSupport[question.type];
    this.state = {
      dirty:false,
      errors: {}
    };
    // if (!formType) {
    //   formType = questionFormMapper.text;
    // }
    // this.state = {
    //   question: question,
		// 	dirty: false,
    //   form: formType
    // }
  }

  setQuestionState(event) {
    //this should call the Action., this should not have any more logic here.,
		this.setState({dirty: true});
		var field = event.target.name;
		var value = event.target.value;
		this.state.question[field] = value;
		return this.setState({question: this.state.question});
	}

  questionFormIsValid() {
    return true;//TODO
  }

  saveQuestion(event) {
		event.preventDefault();

		if (!this.questionFormIsValid()) {
			return;
		}

		if (this.state.question.id) { //TODO - id is not longer meaningful.,
			QuestionActions.updateQuestion(this.state.question);
		} else {
			QuestionActions.createQuestion(this.state.question);
		}

		this.setState({dirty: false});
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
                errors={this.state.errors} />

          </CardText>
        </Card>

      );
  }


}
