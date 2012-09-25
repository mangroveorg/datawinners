from framework.utils.common_utils import by_css

QUESTIONNAIRE_PREVIEW = by_css("#questionnaire_preview_instruction #questionnaire_preview")

PROJECT_NAME = by_css("#questionnaire_preview_instruction .project-name")

INSTRUCTION = by_css("#questionnaire_preview_instruction .preview-instruction")

PREVIEW_STEPS = by_css(".preview-steps")

CLOSE_PREVIEW = by_css(".close_preview")

QUESTION_BY_CSS_LOCATOR = ".preview-steps .olpreview>li:nth-child(%s)"
