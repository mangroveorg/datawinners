"use strict";
import React from 'react';
import BaseQuestions from './base-question-form';

/*
  This can be used for generic question types.
  For customized question type, we can implement similar class.
*/
export default class GenericQuestionForm extends React.Component{
	render() {
		return (
			<form className="form-horizontal">
				{BaseQuestions.getSelectQuestionType(this.props)}
				{BaseQuestions.getDescriptiveQuestions(this.props)}
        {BaseQuestions.getConstraintQuestions(this.props)}
        {BaseQuestions.getControlQuestions(this.props)}
			</form>
		);
	}
};
