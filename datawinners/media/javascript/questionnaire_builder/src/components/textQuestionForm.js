"use strict";

import React from 'react';
import BaseQuestions from './base-question-form';

export default class TextQuestionForm extends React.Component{
	render() {
		return (
			<form key={this.props.question.name} className="form-horizontal">
				{BaseQuestions.getCommonQuestions(this.props)}
			</form>
		);
	}
};
