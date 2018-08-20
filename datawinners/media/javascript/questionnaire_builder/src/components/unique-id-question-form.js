"use strict";

import React from 'react';
import BaseQuestions from './base-question-form';
import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';
import _ from 'lodash';
import QuestionnaireStore from '../store/questionnaire-store';
import AppConstants from '../constants/app-constants';

export default class UniqueIdQuestionForm extends React.Component {
    constructor(props){
      super(props);
    }

    getUniqueIdMenuItems = () => {
      let uniqueId = QuestionnaireStore.getUniqueIdTypes();
      let uniqueIdMenuItems = [];
      _.forEach(uniqueId, function (uniqueId) {
        uniqueIdMenuItems.push(
                                  <MenuItem value={uniqueId}
                                            primaryText={uniqueId}
                                  />
                                );
      });
      return uniqueIdMenuItems;
    }

    render(){
      let questionType = _.split(this.props.question.type,' ');

      return (
        <form className='form-horizontal'>
          {BaseQuestions.getSelectQuestionType(this.props)}
          {BaseQuestions.getDescriptiveQuestions(this.props)}
          <SelectField
                    floatingLabelText={"Constraint " + AppConstants.MANDATORY_ASTERISK}
                    disabled={!this.props.question.isNewQuestion}
                    onChange={this.props.onChangeForUniqueIdType}
                    value={this.props.question.constraint.toLowerCase()}
                    name='constraint'
                    errorText={this.props.errors.type}
                  >
                  {this.getUniqueIdMenuItems()}
          </SelectField>
          {BaseQuestions.getControlQuestions(this.props)}
        </form>
      );
    }
}
