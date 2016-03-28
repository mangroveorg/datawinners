"use strict";

var React = require('react');
// var CommonQuestionFormMixin = require('./commonQuestionFormMixin');

var IntegerQuestionForm = React.createClass({
	// mixins: [CommonQuestionFormMixin],
	render: function() {
		return (
			<form key={this.props.question.name} className="form-horizontal">
        {this.getCommonQuestions()}
			</form>
		);
	}
});

module.exports = IntegerQuestionForm;
