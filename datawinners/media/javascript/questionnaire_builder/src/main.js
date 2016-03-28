import React from 'react';
import ReactDom from 'react-dom';
import QuestionnaireList from './components/questionnaire-list';
import QuestionnaireActions from './actions/questionnaire-actions';
import injectTapEventPlugin from 'react-tap-event-plugin';

// Needed for onTouchTap
// Can go away when react 1.0 release
// Check this repo:
// https://github.com/zilverline/react-tap-event-plugin
injectTapEventPlugin();

ReactDom.render(<QuestionnaireList questionnaire_id={project_id}/>, document.getElementById('questionnaire_builder'));
