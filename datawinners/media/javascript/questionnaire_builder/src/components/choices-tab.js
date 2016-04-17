import React from 'react';
import QuestionnaireActions from '../actions/questionnaire-actions';
import QuestionnaireStore from '../store/questionnaire-store';
import ChoiceGroup from './choice-group';
import FloatingActionButton from 'material-ui/FloatingActionButton';
import ContentAdd from 'material-ui/svg-icons/content/add';

const style = {
	addButtonContainer: {
		position: 'relative',
    bottom: '22px',
    right: '20px',
    float: 'right'
	}
};

export default class ChoicesTab extends React.Component {
  constructor(props){
    super(props);
  }

  onChangeForChoice(choice) {
		QuestionnaireActions.updateChoice(choice);
	}

	onDeleteForChoice(base_index){
		QuestionnaireActions.deleteChoice(base_index);
	}

	onCreateChoice(choiceGroupName, field, value){
		QuestionnaireActions.createChoice(choiceGroupName, field, value);
	}

  getListOfChoiceGroupViews(){
		let choicesGrouped = QuestionnaireStore.getChoicesGrouped();
		let choiceGroupViews = [];
		for (var key in choicesGrouped){
			choiceGroupViews.push(
				<ChoiceGroup
						choiceGroup={choicesGrouped[key]}
						onChangeForChoice={this.onChangeForChoice}
						onDeleteForChoice={this.onDeleteForChoice}
						onCreateChoice={this.onCreateChoice}
						choiceGroupName={key}
						key={'choice_group_'+key}
						/>
			)
		}
		return choiceGroupViews;
	}

  render() {
    if (this.props.currentTab == 'choices') {
      return (
        <div>
          {this.getListOfChoiceGroupViews()}
          <div style={style.addButtonContainer}>
            <FloatingActionButton onMouseDown={this.handleChoiceAddButtonClick}>
              <ContentAdd />
            </FloatingActionButton>
          </div>
        </div>
      );
    } else {
      return (
          <div>This page will be loaded on choices tab</div>
        ); //To optimize performance and minimize DOM content
    }
  }

}
