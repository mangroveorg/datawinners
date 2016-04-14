import React from 'react';
import Card from 'material-ui/lib/card/card';
import CardHeader from 'material-ui/lib/card/card-header';
import CardText from 'material-ui/lib/card/card-text';
import TextField  from 'material-ui/lib/text-field';
import ChoiceItem from './choice-item';

const style = {
  choice_row: {
    background: "#e8eff6",
    borderBottomStyle: "solid",
    borderBottomColor: "grey",
    borderWidth: "2px"
  }
}

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
    var choiceItemViews = []
    for (var item of this.props.choiceGroup){
      choiceItemViews.push(<ChoiceItem choiceItem={item} />);
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
          style={style.choice_row}
        />
        <CardText expandable={true}>
        
          {this.getChoiceItems()}

        </CardText>
      </Card>

    )
  }
}
