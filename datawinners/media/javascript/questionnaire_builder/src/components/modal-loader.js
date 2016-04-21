import React from 'react';
import Dialog from 'material-ui/Dialog';
import FlatButton from 'material-ui/FlatButton';
import RefreshIndicator from 'material-ui/RefreshIndicator';
import RaisedButton from 'material-ui/RaisedButton';

const style = {
  container: {
    position: 'relative',
  },
  refresh: {
    display: 'inline-block',
    position: 'relative',
  },
};

export default class ModalLoader extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      open : props.open,
      label : props.label,
      title : props.title,
      message : props.message,
      cancelLabel : props.cancelLabel,
      onCancel : props.onCancel,
      onOpen : props.onOpen
    };
  }

  onOpen = (event) => {
    this.state.onOpen(event);
    // this.setState({open: true});
  };

  onCancel = () => {
    this.state.onCancel();
    this.props.open = false;
  };

  render() {
    const actions = [
      <FlatButton
        label={this.state.cancelLabel}
        secondary={true}
        onTouchTap={this.onCancel}
      />
    ];

    return (
      <div>
        <RaisedButton label={this.state.label} onTouchTap={this.onOpen} primary={true} />
        <Dialog
          title={this.state.title}
          actions={actions}
          modal={true}
          open={this.props.open}
        >
          {this.state.message}
          <div style={style.container}>
            <RefreshIndicator
              size={60}
              left={270}
              top={15}
              loadingColor={"#FF9800"}
              status="loading"
              style={style.refresh}
            />
          </div>
        </Dialog>
      </div>
    );
  }
}
