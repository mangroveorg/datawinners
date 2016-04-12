import React from 'react';
import QuestionActions from '../actions/questionnaire-actions';
import Toastr from 'toastr';
import Card from 'material-ui/lib/card/card';
import CardHeader from 'material-ui/lib/card/card-header';
import CardText from 'material-ui/lib/card/card-text';
import AppConstants from '../constants/app-constants';
import TextQuestionForm from './text-question-form';
import _ from 'lodash';

const style = {
  question_row: {
    background: "#e8eff6",
    borderBottomStyle: "solid",
    borderBottomColor: "grey",
    borderWidth: "2px"
  }
}

export default class Question extends React.Component {
  constructor(props){
    super(props);
    let question = {};
    this.errors = {};
    if(this.props.question){
      question = this.props.question;
    }

    this.formType = AppConstants.QuestionTypeSupport[question.type];
    this.setQuestionState = this.setQuestionState.bind(this);
    this.setQuestionStateForRequired = this.setQuestionStateForRequired.bind(this);
    this.setQuestionStateForQuestionType = this.setQuestionStateForQuestionType.bind(this);
  }

  setQuestionState(event) {
		let field = event.target.name;
		let value = event.target.value;
    let question = this.props.question;
    question[field] = value;
    this.props.onChange(question);
	}

  //TODO: eventually, we need our own Toggle with name prop
  setQuestionStateForRequired(event) {
    this.props.question['required'] = event.target.value === 'on';
    this.props.onChange(this.props.question);
  }
  //TODO: eventually, we need our own SelectField with name prop
  setQuestionStateForQuestionType(event,index,value){
    this.props.question['type'] = value;
    this.props.onChange(this.props.question);
  }

  questionFormIsValid() {
    return true;//TODO
  }

  render() {
      return (
        <Card>
          <CardHeader
            title={_.truncate(this.props.question.label)}
            subtitle={this.props.question.type}
            actAsExpander={true}
            showExpandableButton={true}
            style={style.question_row}
          />
          <CardText expandable={true}>
              <this.formType
                question={this.props.question}
                onChange={this.setQuestionState}
                errors={this.errors}
                onChangeForRequired={this.setQuestionStateForRequired}
                onChangeForQuestionType={this.setQuestionStateForQuestionType}
                questionTypes={AppConstants.QuestionTypes} //Due to cyclic dependency, passing as param
                />

          </CardText>
        </Card>

      );
  }


}
