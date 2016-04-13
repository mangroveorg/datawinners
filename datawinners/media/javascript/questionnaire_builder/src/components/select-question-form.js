"use strict";

import React from 'react';
import BaseQuestions from './base-question-form';
import SelectField from 'material-ui/lib/select-field';
import MenuItem from 'material-ui/lib/menus/menu-item';

export default class SelectQuestionForm extends React.Component {
    constructor(props){
      super(props);

    }

    onChangeForChoices(event,index,value){

    }

    render(){
      return (
        <form className='form-horizontal'>
          {BaseQuestions.getSelectQuestionType(this.props)}
          <div>
            <SelectField
                      floatingLabelText="Choices..."
                      onChange={this.onChangeForChoices}
                      disabled={!props.question.isNewQuestion}
                      value={props.question.type}
                      name='type'
                      errorText={props.errors.type}
                    >

            </SelectField>
          </div>
        </form>
      );
    }
}
