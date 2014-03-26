from framework.utils.common_utils import by_css, by_xpath

GEN_RANDOM = "gen_random"

NEW_PROJECT_DATA = {'project_name': "new project ", GEN_RANDOM: True}

SELECTED_TEMPLATE_NAME = 'livestock census'
SELECTED_TEMPLATE_QUESTIONS = [u'Date of visit', u'Province', u'District', u'Name of location visited', u'Type of Production', u'Number of Bulls',
     u'Number of Cows', u'Number of Heifers', u'Number of Calves', u'Number of Oxen', u'Number of total cattle',
     u'Number of Sheep', u'Number of Goats', u'Number of Donkeys', u'Number of Horses', u'Number of Poultry']
BLANK_QUESTIONNAIRE_SELECTION_ACCORDION = "#questionnaire_types .questionnaire_type_header:first-child span.header"
SELECT_USING_TEMPLATE_ACCORDION = ".//*[@id='questionnaire_types']/div[4]/span[2]"
AJAX_LOADER_HORIZONTAL = by_css('.ajax-loader-horizontal')
AJAX_LOADER = by_css('.ajax-loader')
TEMPLATE_CATEGORY_ACCORDION = by_css('#questionnaire_template .questionnaire_data')
TEMPLATE_NAME_DIV = by_xpath(".//*[@id='questionnaire_template']//*[text()='livestock census']")
SELECTED_TEMPLATE_QUESTIONS_DIV = by_css('#questionnaire_template_section .selected_questions')
TEMPLATE_NAME_HEADER = by_css('#questionnaire_template_section .project-name-header')
TEMPLATE_QUESTIONS = by_css('#questionnaire_template_section .selected_questions>div>ol>li')






