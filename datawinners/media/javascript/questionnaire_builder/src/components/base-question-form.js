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
import DialogOkayCancel from './dialog-okay-cancel'
import _ from 'lodash';
import AppConstants from '../constants/app-constants';

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

var getQuestionTypeMenuItems = function() {
    var question_type_menu_items = [];
    for (var key in AppConstants.QuestionTypes){
      question_type_menu_items.push(
        <MenuItem
						value={AppConstants.QuestionTypes[key].value}
						primaryText={AppConstants.QuestionTypes[key].label}
						/>
      );
    }
    return question_type_menu_items;
};

module.exports = {

  getSelectQuestionType: function(props){
    let questionType = _.split(props.question.type,' ');

      return (
        <div>
          <SelectField
                    floatingLabelText={"Question Type " + AppConstants.MANDATORY_ASTERISK}
                    onChange={props.onChangeForQuestionType}
                    disabled={!props.question.isNewQuestion}
                    value={questionType[0]}
                    name='type'
                    errorText={props.errors.type}
                  >
                    {getQuestionTypeMenuItems()}
          </SelectField>
          <div style={styles.deleteButton}>
            <DialogOkayCancel label="Delete"
                              icon={<FontIcon className="material-icons" >delete</FontIcon>}
                              onOkay={props.onDelete}
                              title="Are You Sure?"
                              message="You are about to delete the question."
                              okayLabel="I'm Sure"
                              cancelLabel="Cancel" />
          </div>
        </div>

      );
  },
  getDescriptiveQuestions: function(props) {
    return (
      <div>
        <TextField
          floatingLabelText={"Question Label " + AppConstants.MANDATORY_ASTERISK}
          errorText={props.errors.label}
          onChange={props.onChange}
          value={props.question.label}
          name="label"
          multiLine={true}
        />
        <TextField
          floatingLabelText={"Question Name " + AppConstants.MANDATORY_ASTERISK}
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
      </div>
    );
  },
  getControlQuestions: function(props) {
    return (
    <div>
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
          errorText={props.errors.relevant}
          name='relevant'
          onChange={props.onChange}
          value={props.question.relevant}
          multiLine={true}
        />
        <Toggle
          label="Required"
          toggled={_.isEqual(props.question.required,'yes')}
          style={styles.toggle}
          onToggle={props.onChangeForRequired}
        />
      </div>
    );
  },
  getConstraintQuestions: function(props) {
    return (
    <div>
      <TextField
          floatingLabelText="Constraint"
          errorText={props.errors.constraint}
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
      </div>
    );
  }
}
