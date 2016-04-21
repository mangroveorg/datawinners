import React from 'react';
import IconMenu from 'material-ui/IconMenu';
import IconButton from 'material-ui/IconButton';
import FontIcon from 'material-ui/FontIcon';
import RaisedButton from 'material-ui/RaisedButton';
import Toolbar from 'material-ui/Toolbar/Toolbar';
import ToolbarGroup from 'material-ui/Toolbar/ToolbarGroup';
import ToolbarSeparator from 'material-ui/Toolbar/ToolbarSeparator';
import ToolbarTitle from 'material-ui/Toolbar/ToolbarTitle';
import FlatButton from 'material-ui/FlatButton';
import QuestionnaireActions from '../actions/questionnaire-actions';
import MenuItem from 'material-ui/MenuItem';
import DropDownMenu from 'material-ui/DropDownMenu';

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

  onUnderConstruction() {
    alert('Under Construction');
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
          <RaisedButton label="Save Draft" onMouseDown={this.onUnderConstruction}/>
          <ToolbarSeparator />
          <RaisedButton label="Save" primary={true} onMouseDown={this.props.onSave} />
        </ToolbarGroup>
      </Toolbar>
    );
  }
}
