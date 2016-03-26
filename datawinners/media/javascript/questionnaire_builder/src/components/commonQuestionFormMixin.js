"use strict";

var React = require('react');
var Select = require('react-select');
var TextField =require('material-ui/lib/text-field');
var Checkbox =require('material-ui/lib/checkbox');
var Toggle = require('material-ui/lib/toggle');

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

var CommonQuestionFormMixin = {
  propTypes: {
		question:	React.PropTypes.object.isRequired,
		onSave:	React.PropTypes.func.isRequired,
		onChange: React.PropTypes.func.isRequired,
		errors: React.PropTypes.object
	},

  getCommonQuestions: function(){
    return (
      <div>
      <TextField
        floatingLabelText="Question Label"
        errorText={this.props.errors.label}
        onChange={this.props.onChange}
        value={this.props.question.label}
        name="label"
      />
      <TextField
        floatingLabelText="Data Column Name"
        errorText={this.props.errors.name}
        name='name'
        disabled="true"
        onChange={this.props.onChange}
        value={this.props.question.name}
      />
      <TextField
        floatingLabelText="Hint"
        errorText={this.props.errors.hint}
        name='hint'
        onChange={this.props.onChange}
        value={this.props.question.hint}
      />
      <TextField
        floatingLabelText="Constraint"
        errorText={this.props.errors.contraint}
        name='constraint'
        onChange={this.props.onChange}
        value={this.props.question.constraint}
      />
      <TextField
        floatingLabelText="Constraint Message"
        errorText={this.props.errors.constraint_message}
        name='constraint_message'
        onChange={this.props.onChange}
        value={this.props.question.constraint_message}
      />
      <Toggle
        label="Required"
        defaultToggled={true}
        style={styles.toggle}
      />
      </div>
    );
  }

}

module.exports = CommonQuestionFormMixin;
