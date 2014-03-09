from framework.utils.common_utils import by_css

GEN_RANDOM = "gen_random"

NEW_PROJECT_DATA = {'project_name': "new project ", GEN_RANDOM: True}

SELECTED_TEMPLATE_NAME = 'weekly assessment'
SELECTED_TEMPLATE_QUESTIONS = [u'Date', u'District', u'Rainfall', u'Crop Condition', u'Water availability',
                               u'Livestock condition', u'Relief food availability', u'Overall food security situation',
                               u'Local labor availability', u'Major crop of the district',
                               u'Market price of the major crop of the district (per qt)',
                               u'New cases of severe acute malnutrition (SAM) seen at Health Center']

BLANK_QUESTIONNAIRE_SELECTION_ACCORDION = ".//*[@id='questionnaire_types']/div[1]/span[2]"
SELECT_USING_TEMPLATE_ACCORDION = ".//*[@id='questionnaire_types']/div[4]/span[2]"
AJAX_LOADER_HORIZONTAL = by_css('.ajax-loader-horizontal')
AJAX_LOADER = by_css('.ajax-loader')
TEMPLATE_CATEGORY_ACCORDION = by_css('#questionnaire_template .template_data')
TEMPLATE_NAME_DIV = by_css('#questionnaire_template .template_name')
SELECTED_TEMPLATE_QUESTIONS_DIV = by_css('.selected_questions')
TEMPLATE_NAME_HEADER = by_css('.project-name-header')
TEMPLATE_QUESTIONS = by_css('.selected_questions>div>ol>li')






