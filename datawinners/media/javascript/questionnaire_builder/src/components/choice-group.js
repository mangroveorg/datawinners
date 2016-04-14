import React from 'react';
import Card from 'material-ui/lib/card/card';
import CardHeader from 'material-ui/lib/card/card-header';
import CardText from 'material-ui/lib/card/card-text';
import TextField  from 'material-ui/lib/text-field';
import ChoiceItem from './choice-item';

import Table from 'material-ui/lib/table/table';
import TableHeaderColumn from 'material-ui/lib/table/table-header-column';
import TableRow from 'material-ui/lib/table/table-row';
import TableHeader from 'material-ui/lib/table/table-header';
import TableRowColumn from 'material-ui/lib/table/table-row-column';
import TableBody from 'material-ui/lib/table/table-body';

const styles = {
  choice_row: {
    background: "#BBBBBB",
    borderBottomStyle: "solid",
    borderBottomColor: "grey",
    borderWidth: "2px",
    height:'initial'
  }
};

export default class ChoiceGroup extends React.Component {
  constructor(props){
    super(props);
    this.errors = {};

  }

  onChange(event) {
    //TODO - this needs refactoring..
		let field = event.target.name;
		let value = event.target.value;
    let choiceGroup = this.props.choiceGroup;
    choiceGroup[field] = value;
    // this.setState({choice: choice});
    // this.props.onChange(choice);
	}

  getChoiceItems(){
    var choiceItemViews = [];
    // let striped = true;
    for (var choiceItem of this.props.choiceGroup){
      // choiceItemViews.push(<ChoiceItem choiceItem={item} />);
      // striped = !striped;
      choiceItemViews.push(
        <TableRow>
          <TableRowColumn displayBorder={false}>{choiceItem.name}
          </TableRowColumn>
          <TableRowColumn displayBorder={false}>{choiceItem.label}
          </TableRowColumn>
        </TableRow>
      );
    }
    return choiceItemViews;
  }


  render(){
    return (
      <Card>
        <CardHeader
          title={_.truncate(this.props.choiceGroup[0]['list name'])}
          actAsExpander={true}
          showExpandableButton={true}
          style={styles.choice_row}
        />
        <CardText expandable={true}>
          <TextField
            floatingLabelText="List name"
            errorText={this.errors['list name']}
            onChange={this.onChange}
            disabled={true}
            value={this.props.choiceGroup[0]['list name']}
            name="name"
            multiLine={true}
          />

          <Table className='builder-choice-group-table' >
            <TableHeader displaySelectAll={false} selectable={false}>
              <TableRow displayBorder={false}>
                <TableHeaderColumn>Name</TableHeaderColumn>
                <TableHeaderColumn>Label</TableHeaderColumn>
              </TableRow>
            </TableHeader>
            <TableBody>
              {this.getChoiceItems()}
            </TableBody>
          </Table>
        </CardText>
      </Card>

    )
  }
}
