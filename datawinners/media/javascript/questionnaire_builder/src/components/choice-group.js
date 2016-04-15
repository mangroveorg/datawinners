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
    background: "#e8eff6",
    borderTopStyle: "solid",
    borderTopColor: "grey",
    borderWidth: "2px",
    height:'initial'
  },
  table: {
    marginBottom: '0px',
    borderBottomWidth:'0px',
    borderBottomStyle: "none",
    borderWidth: "0px"
  },
  table_td: {
    border: 'none',
    padding: '0px',
    borderBottomWidth:'0px',
    borderBottomStyle: "none",
    borderWidth: "0px"
  },
  table_th:{
    fontWeight: 'bold',
    padding: '0px',
    borderBottomWidth:'0px',
    borderBottomStyle: "none",
    borderWidth: "0px"

  },
  table_tr:{
    border: 'none',
    borderBottomWidth:'0px',
    borderBottomStyle: "none",
    borderWidth: "0px"

  },
  headerStyle: {
    height:'20px'
  },
  choiceTextField:{
    width: '100%'
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
    return this.props.choiceGroup.map((choiceItem) => (
      <TableRow style={styles.table_tr} selectable={false}>
        <TableRowColumn style={styles.table_td} displayBorder={false}  >
          <TextField
            name='name'
            value={choiceItem.name}
            style={styles.choiceTextField}
          />

        </TableRowColumn>
        <TableRowColumn style={styles.table_td} displayBorder={false}>
        <TextField
          name='label'
          value={choiceItem.label}
          style={styles.choiceTextField}
        />
        </TableRowColumn>
      </TableRow>
    ));
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
          <br/><br/><br/>

          <Table className='builder-choice-group-table'
                  style={styles.table}
                  headerStyle={styles.headerStyle}
                  >
            <TableHeader displaySelectAll={false} style={styles.table_th} adjustForCheckbox={false}>
              <TableRow selectable={false} style={styles.table_tr}>
                <TableHeaderColumn style={styles.table_td}>Name</TableHeaderColumn>
                <TableHeaderColumn style={styles.table_td}>Label</TableHeaderColumn>
              </TableRow>
            </TableHeader>
            <TableBody displayRowCheckbox={false}>
              {this.getChoiceItems()}
            </TableBody>
          </Table>
        </CardText>
      </Card>
    )
  }
}
