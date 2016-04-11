"use strict";

import React  from 'react';
import Select  from 'react-select';
import TextField  from 'material-ui/lib/text-field';
import Checkbox  from 'material-ui/lib/checkbox';
import Toggle  from 'material-ui/lib/toggle';

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

module.exports = {
  getCommonQuestions: function(props){
    return (
      <div>
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
        disabled={true}
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
