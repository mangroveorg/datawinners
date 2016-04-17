import React from 'react';
import ReactDom from 'react-dom';
import "babel-polyfill";
import QuestionnaireList from './components/questionnaire-list';
import injectTapEventPlugin from 'react-tap-event-plugin';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import getMuiTheme from 'material-ui/styles/getMuiTheme';

// Needed for onTouchTap
// Can go away when react 1.0 release
// Check this repo:
// https://github.com/zilverline/react-tap-event-plugin
injectTapEventPlugin();

class Main extends React.Component {
  render() {
    return (
      <MuiThemeProvider muiTheme={getMuiTheme()}>
        <QuestionnaireList questionnaire_id={project_id}/>
      </MuiThemeProvider>
    );
  }
}

ReactDom.render(<Main />, document.getElementById('questionnaire_builder'));
