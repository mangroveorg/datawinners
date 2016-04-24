import React from 'react';
import QuestionnaireActions from '../actions/questionnaire-actions';
import QuestionnaireStore from '../store/questionnaire-store';
import FloatingActionButton from 'material-ui/FloatingActionButton';
import ContentAdd from 'material-ui/svg-icons/content/add';
import {Table, TableBody, TableHeader, TableHeaderColumn, TableRow, TableRowColumn}
        from 'material-ui/Table';
import TextField from 'material-ui/TextField';
import CascadeGroup from './cascade-group';

const styles = {
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

};

export default class CascadesTab extends React.Component {
  constructor(props){
    super(props);
  }

  render() {
    let cascadeGroupViews = this.props.cascadesGrouped.map((cascadeGroup)=>(
      <CascadeGroup cascadeGroup={cascadeGroup}/>
    ));
    return (
      <div>
      {cascadeGroupViews}
      </div>
    );
  }
}
