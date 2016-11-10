def _get_value(values, question_path_components):
    if len(question_path_components) == 1:
        return values[question_path_components[0]]
    return _get_value(values[question_path_components[0]][0], question_path_components[1:])


def resolve_data(variables, data):
    resolved_data = []
    for variable in variables:
        questionnaire_alias = variable.split(".")[0]
        question_path_components = variable.split(".")[1:]
        for index, datum in enumerate(data):
            value = _get_value(datum[questionnaire_alias].value["values"], question_path_components)
            len(resolved_data) > index or resolved_data.append({})
            resolved_data[index][variable] = value
    return resolved_data
