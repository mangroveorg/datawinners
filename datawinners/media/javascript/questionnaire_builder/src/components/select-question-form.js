"use strict";

import React from 'react';
import BaseQuestions from './base-question-form';
import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';
import _ from 'lodash';
import QuestionnaireStore from '../store/questionnaire-store';
import AppConstants from '../constants/app-constants';

export default class SelectQuestionForm extends React.Component {
    constructor(props){
      super(props);

    }

    getChoicesMenuItems = () => {
      let choicesMenuItems = [];
      let choicesGrouped = QuestionnaireStore.getChoicesGrouped();
      for (var key in choicesGrouped){
        choicesMenuItems.push(
          <MenuItem
  						value={key}
  						primaryText={key}
  						/>
        );
      }
      return choicesMenuItems;

    }

    render(){
      let questionType = _.split(this.props.question.type,' ');

      return (
        <form className='form-horizontal'>
          {BaseQuestions.getSelectQuestionType(this.props)}
          <div>
            <SelectField
                      floatingLabelText={"Choices " + AppConstants.MANDATORY_ASTERISK}
                      onChange={this.props.onChangeForChoiceType}
                      value={questionType[1]}
                      name='choiceType'
                      errorText={this.props.errors.choiceType}
                    >
                    {this.getChoicesMenuItems()}
            </SelectField>
          </div>
          {BaseQuestions.getDescriptiveQuestions(this.props)}
          {BaseQuestions.getConstraintQuestions(this.props)}
          {BaseQuestions.getControlQuestions(this.props)}
        </form>
      );
    }
}
