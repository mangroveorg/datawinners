from datawinners.blue.rules.rule import Rule


class RemoveRule(Rule):
    def update_submission(self, submission):
        return True

    def change_mapping(self):
        return True

    def remove(self):
        pass

    def edit(self, node, old_field, new_field):
        pass
