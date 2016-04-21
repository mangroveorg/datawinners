import React from 'react';
import QuestionActions from '../actions/questionnaire-actions';
import Toastr from 'toastr';
import Card from 'material-ui/Card/Card';
import CardHeader from 'material-ui/Card/CardHeader';
import CardText from 'material-ui/Card/CardText';
import AppConstants from '../constants/app-constants';
import FormFactory from './form-factory';
import _ from 'lodash';
import Paper from 'material-ui/Paper';

const style = {
  question_row: {
    background: "#e8eff6",
    borderTopStyle: "solid",
    borderTopColor: "grey",
    borderWidth: "2px"
  }
}

export default class Question extends React.Component {
  constructor(props){
    super(props);
    this.formType = FormFactory.getFormForQuestionType(this.props.question.type);
  }

  onChange = (event) => {
		let field = event.target.name;
		let value = event.target.value;
    let question = this.props.question;
    question[field] = value;
    this.props.onChange(question);
	}

  //TODO: eventually, we need our own Toggle with name prop
  onChangeForRequired = (event) => {
    this.props.question['required'] = event.target.value === 'on' ? 'yes' : 'no';
    this.props.onChange(this.props.question);
  }
  //TODO: eventually, we need our own SelectField with name prop
  onChangeForQuestionType = (event,index,value) => {
    this.props.question['type'] = value;
    this.props.onChange(this.props.question);
    this.formType = FormFactory.getFormForQuestionType(value);
  }

  onChangeForChoiceType = (event,index,value) => {
    let questionType = _.split(this.props.question.type,' ');
    questionType[1] = value;
    this.props.question['type'] = _.join(questionType, ' ');
    this.props.onChange(this.props.question);
  }

  onChangeForUniqueIdType = (event, index, value) => {
    this.props.question['constraint'] = value;
    this.props.onChange(this.props.question);
  }

  questionFormIsValid() {
    return true;//TODO
  }

  onDelete = (event) => {
    this.props.onDelete(this.props.question);
  }

  render() {
      return (
        <Card>
          <CardHeader
            title={_.truncate(this.props.question.label , {'length': 100})}
            subtitle={this.props.question.type}
            actAsExpander={true}
            showExpandableButton={true}
            style={style.question_row}
          />
          <CardText expandable={true}>
              <this.formType
                question={this.props.question}
                onChange={this.onChange}
                errors={this.props.errors}
                onChangeForRequired={this.onChangeForRequired}
                onChangeForQuestionType={this.onChangeForQuestionType}
                onChangeForChoiceType={this.onChangeForChoiceType}
                onChangeForUniqueIdType={this.onChangeForUniqueIdType}
                onDelete={this.onDelete}
                questionTypes={AppConstants.QuestionTypes} //Due to cyclic dependency, passing as param
                />
            </CardText>
        </Card>

      );
  }


}
