"use strict";
import React  from 'react';
import Select  from 'react-select';
import TextField  from 'material-ui/lib/text-field';
import Checkbox  from 'material-ui/lib/checkbox';
import Toggle  from 'material-ui/lib/toggle';
import SelectField from 'material-ui/lib/select-field';
import MenuItem from 'material-ui/lib/menus/menu-item';

const styles = {
  block: {
    maxWidth: 250,
  },
  toggle: {
    maxWidth: 150,
    marginBottom: 16,
    fontWeight: 'normal'
  },
};

var getQuestionTypeMenuItems = function(questionTypes) {
    var question_type_menu_items = [];
    for (var key in questionTypes){
      question_type_menu_items.push(
        <MenuItem
						value={questionTypes[key].value}
						primaryText={questionTypes[key].label}
						/>
      );
    }
    return question_type_menu_items;
};

module.exports = {

  getSelectQuestionType: function(props, questionTypes){
      return (
        <div>
        <SelectField
                  floatingLabelText="Question Type"
                  onChange={props.onChangeForQuestionType}
                  disabled={!props.question.isNewQuestion}
                  value={props.question.type}
                  name='type'
                  errorText={props.errors.type}
                >
                  {getQuestionTypeMenuItems(props.questionTypes)}
        </SelectField>
        </div>

      );
  },

  getCommonQuestions: function(props, questionTypes){
    return (
      <div>
        {this.getSelectQuestionType(props, questionTypes)}
      <TextField
        floatingLabelText="Question Label"
        errorText={props.errors.label}
        onChange={props.onChange}
        value={props.question.label}
        name="label"
        multiLine={true}
      />
      <TextField
        floatingLabelText="Data Column Name"
        errorText={props.errors.name}
        name='name'
        disabled={!props.question.isNewQuestion}
        onChange={props.onChange}
        value={props.question.name}
        multiLine={true}
      />
      <TextField
        floatingLabelText="Hint"
        errorText={props.errors.hint}
        name='hint'
        onChange={props.onChange}
        value={props.question.hint}
        multiLine={true}
      />
      <TextField
        floatingLabelText="Constraint"
        errorText={props.errors.contraint}
        name='constraint'
        onChange={props.onChange}
        value={props.question.constraint}
        multiLine={true}
      />
      <TextField
        floatingLabelText="Constraint Message"
        errorText={props.errors.constraint_message}
        name='constraint_message'
        onChange={props.onChange}
        value={props.question.constraint_message}
        multiLine={true}
      />
      <TextField
        floatingLabelText="Appearance"
        errorText={props.errors.appearance}
        name='appearance'
        onChange={props.onChange}
        value={props.question.appearance}
        multiLine={true}
      />
      <TextField
        floatingLabelText="Relevant"
        errorText={props.errors.relavant}
        name='relavant'
        onChange={props.onChange}
        value={props.question.relavant}
        multiLine={true}
      />
      <Toggle
        label="Required"
        defaultToggled={props.question.required == true}
        style={styles.toggle}
        onToggle={props.onChangeForRequired}
      />
      </div>
    );
  }
}
