var SampleQuestionnaire = {
		  questions: [
		              {
		                name: 'name1',
		                label: 'What is your name?',
		                id: 'name1',
		                type: 'text',
		                hint:'Answer must fit on one line',
		                required: 'yes'
		              },
		              {
		                name: 'age1',
		                label: 'What is your age?',
		                id: 'age1',
		                type: 'integer',
		                hint:'As per records',
		                required: 'yes'
		              },
		              {
		                name: 'weight',
		                label: 'What is your Weight?',
		                id: 'weight',
		                type: 'decimal',
		                hint:'As per records',
		                required: 'yes'
		              },
		              {
		                name: 'dob',
		                label: 'What is your date of birth?',
		                id: 'dob',
		                type: 'date',
		                hint:'As per records',
		                required: 'yes'
		              }


		            ]
		          };

module.exports = SampleQuestionnaire;