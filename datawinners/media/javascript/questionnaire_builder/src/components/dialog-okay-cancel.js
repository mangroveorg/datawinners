import React from 'react';
import Dialog from 'material-ui/Dialog';
import FlatButton from 'material-ui/FlatButton';
import RaisedButton from 'material-ui/RaisedButton';

export default class DialogOkayCancel extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      open : false,
      onOkay : props.onOkay,
      icon : props.icon,
      label : props.label || "Open Dialog",
      title : props.title || "",
      message : props.message || "",
      cancelLabel : props.cancelLabel || "Cancel",
      okayLabel : props.okayLabel || "Okay"
    };
  }

  onOpen = () => {
    this.setState({open: true});
  };

  onClose = () => {
    this.setState({open: false});
  };

  onOkay = () => {
    if (this.state.onOkay) {
      this.state.onOkay();
    }
    this.onClose();
  };

  render() {
    const actions = [
      <FlatButton
        label={this.state.cancelLabel}
        secondary={true}
        onTouchTap={this.onClose}
      />,
      <FlatButton
        label={this.state.okayLabel}
        primary={true}
        onTouchTap={this.onOkay}
      />,
    ];

    return (
      <div>
        <RaisedButton label={this.state.label} icon={this.state.icon} onTouchTap={this.onOpen} />
        <Dialog
          title={this.state.title}
          actions={actions}
          modal={false}
          open={this.state.open}
          onRequestClose={this.onClose}
        >
          {this.state.message}
        </Dialog>
      </div>
    );
  }
}
