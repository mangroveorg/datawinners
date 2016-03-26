import React from 'react';
import ReactDom from 'react-dom';
import QuestionnaireList from './components/questionnaire-list';
import QuestionnaireActions from './actions/questionnaire-actions';

// QuestionnaireActions.initQuestionnaire();

ReactDom.render(<QuestionnaireList questionnaire_id={project_id}/>, document.getElementById('questionnaire_builder'));
