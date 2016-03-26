import React from 'react';
import TextQuestionForm from './textQuestionForm';
import IntegerQuestionForm from './integerQuestionForm';
import DateQuestionForm from './dateQuestionForm';
import DecimalQuestionForm from './decimalQuestionForm';
import QuestionActions from '../actions/questionnaire-actions';
import Toastr from 'toastr';
import Card from 'material-ui/lib/card/card';
import CardHeader from 'material-ui/lib/card/card-header';
import CardText from 'material-ui/lib/card/card-text';

var questionFormMapper = {
  'text' : TextQuestionForm,
  'date' : DateQuestionForm,
  'integer' : IntegerQuestionForm,
  'decimal' : DecimalQuestionForm
};

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
    this.state = {
      question,
      errors: {},
			dirty: false,
      form: questionFormMapper[question.type]
    }
  }

  setQuestionState(event) {
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

		if (this.state.question.id) {
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
            style={{"background": "azure",
                   "borderBottomStyle": "solid",
                   "borderBottomColor": "grey"}}
          />
          <CardText expandable={true}>
              <this.state.form
                question={this.state.question}
                onChange={this.setQuestionState}
                onSave={this.saveQuestion}
                errors={this.state.errors} />

          </CardText>
        </Card>


      );
  }


}
