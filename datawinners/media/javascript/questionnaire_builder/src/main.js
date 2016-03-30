import React from 'react';
import ReactDom from 'react-dom';
import QuestionnaireList from './components/questionnaire-list';
import QuestionnaireActions from './actions/questionnaire-actions';
import injectTapEventPlugin from 'react-tap-event-plugin';
import darkBaseTheme from 'material-ui/lib/styles/baseThemes/darkBaseTheme';
import MuiThemeProvider from 'material-ui/lib/MuiThemeProvider';
import getMuiTheme from 'material-ui/lib/styles/getMuiTheme';
import {grey700} from 'material-ui/lib/styles/colors';

// const darkMuiTheme = getMuiTheme(darkBaseTheme);
// Needed for onTouchTap
// Can go away when react 1.0 release
// Check this repo:
// https://github.com/zilverline/react-tap-event-plugin
injectTapEventPlugin();

const darkMuiTheme = getMuiTheme({
  // palette: {
  //   textColor: cyan500,
  // },
  appBar: {
    height: 40,
    color: grey700
  },
});

class Main extends React.Component {
  render() {
    return (
      <MuiThemeProvider muiTheme={darkMuiTheme}>
        <QuestionnaireList questionnaire_id={project_id}/>
      </MuiThemeProvider>
    );
  }
}

ReactDom.render(<Main />, document.getElementById('questionnaire_builder'));
