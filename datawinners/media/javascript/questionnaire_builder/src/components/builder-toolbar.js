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
import MenuItem from 'material-ui/lib/menus/menu-item';
import DropDownMenu from 'material-ui/lib/DropDownMenu';

export default class BuilderToolbar extends React.Component {

  constructor(props) {
    super(props);
  }

  onUpload() {
    $("input[name=file]").click();
  }

  onDownload() {
    $('#download_form').attr('action', '/xlsform/download/').submit();
  }

  render() {
    return (
      <Toolbar>
        <ToolbarGroup float='left'>
          <RaisedButton label="Upload"
                onMouseDown={this.onUpload}
                icon={<FontIcon className="material-icons" tooltip="upload questionnaire excel"
                tooltipPosition="top-center" >file_upload</FontIcon>} />
          <RaisedButton
            label="Download"
            onMouseDown={this.onDownload}
            icon={<FontIcon className="material-icons" tooltip="download questionnaire excel"
            tooltipPosition="top-center" >file_download</FontIcon>} />
        </ToolbarGroup>
        <ToolbarGroup float="right">
          <RaisedButton label="Save Draft" onMouseDown={this.onDownload}/>
          <ToolbarSeparator />
          <RaisedButton label="Save" primary={true} onMouseDown={this.props.onSave} />
        </ToolbarGroup>
      </Toolbar>
    );
  }
}
