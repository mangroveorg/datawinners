from datawinners.questionnaire.library import QuestionnaireLibrary


def create_questionnaire_templates():
    library = QuestionnaireLibrary()
    docs = library.create_template_from_project("template_data.json")
    print docs

create_questionnaire_templates()