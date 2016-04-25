import React from 'react';
import Card from 'material-ui/Card/Card';
import CardHeader from 'material-ui/Card/CardHeader';
import CardText from 'material-ui/Card/CardText';
import TextField from 'material-ui/TextField';

import {Table, TableBody, TableHeader, TableHeaderColumn, TableRow, TableRowColumn}
        from 'material-ui/Table';

import FontIcon from 'material-ui/FontIcon';
import FlatButton from 'material-ui/FlatButton';
import _ from 'lodash';


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
  table_th: {
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

const BUILDER_CHOICE_ID_PREFIX = 'builder_choice_';

export default class ChoiceGroup extends React.Component {
  constructor(props){
    super(props);
    this.errors = {};
  }

  onChange = (event) => {
		let field = event.target.name;
		let value = event.target.value;
    let base_index = _.replace(event.target.id,BUILDER_CHOICE_ID_PREFIX,'');
    let index = _.findIndex(this.props.choiceGroup, {base_index: base_index});
    if (index >= 0) {
      let choice = this.props.choiceGroup[index];
      choice[field] = value;
      this.props.onChangeForChoice(choice);
    } else {
      this.props.onCreateChoice(this.props.choiceGroupName, field, value);
    }
	};

  onDelete = (event) => {
    let id = event.currentTarget.id;
    let base_index = _.replace(id,BUILDER_CHOICE_ID_PREFIX,'');
    this.props.onDeleteForChoice(base_index);
  }

  getChoiceItems(){
    let choiceItems = this.props.choiceGroup.map((choiceItem) => (
      <TableRow style={styles.table_tr} selectable={false}
                key={BUILDER_CHOICE_ID_PREFIX+choiceItem.base_index}>
        <TableRowColumn style={styles.table_td} displayBorder={false}  >
          <TextField
            name='name'
            id={BUILDER_CHOICE_ID_PREFIX+choiceItem.base_index}
            value={choiceItem.name}
            style={styles.choiceTextField}
            errorText = {this.props.errors[choiceItem.base_index] ? this.props.errors[choiceItem.base_index].name : ''}
            onChange={this.onChange}
          />

        </TableRowColumn>
        <TableRowColumn style={styles.table_td} displayBorder={false}>
        <TextField
          name='label'
          id={'builder_choice_'+choiceItem.base_index}
          value={choiceItem.label}
          style={styles.choiceTextField}
          errorText = {this.props.errors[choiceItem.base_index] ? this.props.errors[choiceItem.base_index].label : ''}
          onChange={this.onChange}
        />
        </TableRowColumn>
        <TableRowColumn style={styles.table_td} displayBorder={false}>
          <FlatButton
            id={'builder_choice_'+choiceItem.base_index}
            label="Delete"
            onMouseDown={this.onDelete}
            icon={<FontIcon className="material-icons" >delete</FontIcon>}
          />
        </TableRowColumn>
      </TableRow>
    ));
    choiceItems.push(
      <TableRow style={styles.table_tr} selectable={false}
            key={"new_choice_for_choice_group"+this.props.choiceGroupName}>
        <TableRowColumn style={styles.table_td} displayBorder={false} >
          <TextField
            id={'new_choice_name'}
            hintText='Name'
            name='name'
            style={styles.choiceTextField}
            onChange={this.onChange}
          />

        </TableRowColumn>
        <TableRowColumn style={styles.table_td} displayBorder={false}>
        <TextField
          id={'new_choice_label'}
          hintText='Label'
          name='label'
          style={styles.choiceTextField}
          onChange={this.onChange}
        />
        </TableRowColumn>
        <TableRowColumn style={styles.table_td} displayBorder={false}>

        </TableRowColumn>
      </TableRow>

    );
    return choiceItems;
  }

  render(){
    return (
      <Card key={'builder_choice_'+this.props.choiceGroup[0].base_index}>
        <CardHeader
          title={_.truncate(this.props.choiceGroupName)}
          actAsExpander={true}
          showExpandableButton={true}
          style={styles.choice_row}
        />
        <CardText expandable={true}>
          <TextField
            id={'builder_choice_'+this.props.choiceGroup[0].base_index}
            floatingLabelText="List name"
            onChange={this.onChange}
            errorText = {this.props.choiceGroup[0].base_index && this.props.errors[this.props.choiceGroup[0].base_index] ? this.props.errors[this.props.choiceGroup[0].base_index].list_name : ''}
            disabled={!this.props.isNewChoiceGroup}
            value={this.props.choiceGroupName}
            name="list_name"
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
                <TableHeaderColumn style={styles.table_td}></TableHeaderColumn>
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
