import React  from 'react';
import Select  from 'react-select';
import TextField from 'material-ui/TextField';
import Checkbox from 'material-ui/Checkbox';
import Toggle from 'material-ui/Toggle';
import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';
import RaisedButton from 'material-ui/RaisedButton';
import FontIcon from 'material-ui/FontIcon';
import IconButton from 'material-ui/IconButton';
import QuestionnaireActions from '../actions/questionnaire-actions';

const styles = {
  block: {
    maxWidth: 250,
  },
  toggle: {
    maxWidth: 150,
    marginBottom: 16,
    fontWeight: 'normal'
  },
  deleteButton: {
    float: 'right',
    display: 'block'
  }
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
          <RaisedButton label="Delete"
                onMouseDown={props.onDelete}
                style={styles.deleteButton}
                icon={<FontIcon className="material-icons" >delete</FontIcon>} />
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
