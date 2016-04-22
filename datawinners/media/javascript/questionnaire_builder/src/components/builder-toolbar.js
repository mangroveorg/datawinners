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
import AppConstants from '../constants/app-constants';
import LoaderDialog from './loader-dialog';
import QuestionnaireStore from '../store/questionnaire-store';

export default class BuilderToolbar extends React.Component {

  constructor(props) {
    super(props);
    this.state={
                 isLoading: false,
                 message: ''
               };
  }

  onLoading = (message) => {
    this.setState({
                    isLoading: true,
                    message: message
                  });
  }

  onLoadingComplete = () => {
    this.setState({isLoading: false});
  }

  onUpload = () => {
    self = this;
    $("input[name=file]").change(function() {
      // self.onLoading(AppConstants.LoaderMessages.UPLOAD_MESSAGE);
      console.log('upload completed');
    });

    //$('.ui-dialog .ui-widget .ui-widget-content').waypoint(function() {
      // self.onLoadingComplete();
     //console.log('upload done');
    //});

    $("input[name=file]").click();
  }

  onDownload = () => {
    $('#download_form').attr('action', '/xlsform/download/').submit();
  }

  onSave = () => {
    this.onLoading(AppConstants.LoaderMessages.SAVE_MESSAGE);
    //TODO - should take questionnaire from store, not from here
    let status = QuestionnaireActions.saveQuestionnaire (
                                                          QuestionnaireStore.getQuestionnaireId(),
                                                          QuestionnaireStore.getQuestionnaire(),
                                                          QuestionnaireStore.getFileType(),
                                                          this.onSaveComplete
                                                        );
  }

  onSaveComplete = () => {
    this.onLoadingComplete();
  }

  onUnderConstruction = () => {
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
          <RaisedButton label="Save" onTouchTap={this.onSave} primary={true} />
          <LoaderDialog open={this.state.isLoading}
                       title="Please Wait.."
                       message={this.state.message} />
        </ToolbarGroup>
      </Toolbar>
    );
  }
}
