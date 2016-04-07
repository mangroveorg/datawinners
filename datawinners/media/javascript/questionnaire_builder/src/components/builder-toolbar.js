import React from 'react';
import IconMenu from 'material-ui/lib/menus/icon-menu';
import IconButton from 'material-ui/lib/icon-button';
import FontIcon from 'material-ui/lib/font-icon';
import RaisedButton from 'material-ui/lib/raised-button';
import Toolbar from 'material-ui/lib/toolbar/toolbar';
import ToolbarGroup from 'material-ui/lib/toolbar/toolbar-group';
import ToolbarSeparator from 'material-ui/lib/toolbar/toolbar-separator';
import ToolbarTitle from 'material-ui/lib/toolbar/toolbar-title';
import FlatButton from 'material-ui/lib/flat-button';
import ActionAndroid from 'material-ui/lib/svg-icons/action/android';
import QuestionnaireActions from '../actions/questionnaire-actions';

export default class BuilderToolbar extends React.Component {

  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Toolbar>
        <ToolbarGroup float='left'>
          <FlatButton
            label="Survey"
            labelPosition="after"
            icon={<ActionAndroid />}
            disabled={true}
          />
          <FlatButton
            label="Choices"
            labelPosition="after"
            icon={<ActionAndroid />}
          />
          <FlatButton
            label="Cascades"
            labelPosition="after"
            icon={<ActionAndroid />}
          />
        </ToolbarGroup>
        <ToolbarGroup float="right">
          <ToolbarSeparator />
          <RaisedButton label="Save" primary={true} onMouseDown={this.props.onSave} />
        </ToolbarGroup>
      </Toolbar>
    );
  }
}
