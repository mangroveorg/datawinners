from datawinners.blue import rules


class XFormEditor(object):
    def edit(self, new_questionnaire, old_questionnaire):
        self._validate(new_questionnaire, old_questionnaire)

    def _validate(self, new_questionnaire, old_questionnaire):
        [rule.update_xform(new_questionnaire, old_questionnaire) for rule in rules.REGISTERED_RULES]

    def _apply(self):
        pass

# questionnaire.save(process_post_update=False)
