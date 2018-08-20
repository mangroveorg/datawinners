import React from 'react';
import Card from 'material-ui/Card/Card';
import CardHeader from 'material-ui/Card/CardHeader';
import CardText from 'material-ui/Card/CardText';
import TextField from 'material-ui/TextField';

const styles = {
  cascades_row: {
    background: "#e8eff6",
    borderTopStyle: "solid",
    borderTopColor: "grey",
    borderWidth: "2px",
    height:'initial'
  }
}

export default class CascadeGroup extends React.Component {
  render() {
      return (
        <Card>
          <CardHeader
            title={_.truncate(this.props.cascadeGroup.label)}
            subtitle={this.props.cascadeGroup.name}
            actAsExpander={true}
            showExpandableButton={true}
            style={styles.cascades_row}
          />
          <CardText expandable={true}>
            <TextField
              id={'builder_choice_'}
              floatingLabelText="Name"
              value={this.props.cascadeGroup.name}
              name="name"
              multiLine={true}
            />
            <TextField
              id={'builder_choice_'}
              floatingLabelText="Label"
              value={this.props.cascadeGroup.label}
              name="label"
              multiLine={true}
            />
            <br/><br/><br/>
            </CardText>
          </Card>
      );
  }
}
