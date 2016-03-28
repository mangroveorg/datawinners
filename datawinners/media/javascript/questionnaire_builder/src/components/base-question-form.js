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
      />
      <TextField
        floatingLabelText="Data Column Name"
        errorText={props.errors.name}
        name='name'
        disabled={true}
        onChange={props.onChange}
        value={props.question.name}
      />
      <TextField
        floatingLabelText="Hint"
        errorText={props.errors.hint}
        name='hint'
        onChange={props.onChange}
        value={props.question.hint}
      />
      <TextField
        floatingLabelText="Constraint"
        errorText={props.errors.contraint}
        name='constraint'
        onChange={props.onChange}
        value={props.question.constraint}
      />
      <TextField
        floatingLabelText="Constraint Message"
        errorText={props.errors.constraint_message}
        name='constraint_message'
        onChange={props.onChange}
        value={props.question.constraint_message}
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
// export default class BaseQuestionForm extends React.Component {
//     constructor(props){
//       super(props);
//     }
//     render(){
//       return <h3>Inside Base question form</h3>;
//     }
// }
//
// BaseQuestionForm.propTypes = {
//   question:	React.PropTypes.object.isRequired,
//   onSave:	React.PropTypes.func.isRequired,
//   onChange: React.PropTypes.func.isRequired,
//   errors: React.PropTypes.object
// };

// module.exports = BaseQuestions;
