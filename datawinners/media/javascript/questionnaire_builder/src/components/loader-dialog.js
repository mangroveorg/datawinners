import React from 'react';
import Dialog from 'material-ui/Dialog';
import FlatButton from 'material-ui/FlatButton';
import RefreshIndicator from 'material-ui/RefreshIndicator';
import RaisedButton from 'material-ui/RaisedButton';

const style = {
  customContentStyle: {
    width: '33%'
  },
  container: {
    position: 'relative'
  },
  refresh: {
    display: 'inline-block',
    position: 'relative',
  },
};

export default class LoaderDialog extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      open : props.open,
      title : props.title,
      message : props.message,
      cancelLabel : props.cancelLabel,
      onCancel : props.onCancel
    };
  }

  onOpen = (event) => {
    this.state.onOpen(event);
  };

  onCancel = () => {
    this.state.onCancel();
    this.props.open = false;
  };

  render() {
    return (
      <div>
        <Dialog
          title={this.state.title}
          modal={true}
          open={this.props.open}
          contentStyle={style.customContentStyle}
        >
          {this.props.message}
          <div style={style.container}>
            <RefreshIndicator
              size={50}
              left={145}
              top={10}
              status="loading"
              style={style.refresh}
            />
          </div>
        </Dialog>
      </div>
    );
  }
}
