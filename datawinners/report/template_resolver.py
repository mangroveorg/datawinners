def resolve_data(variables, data):
    resolved_data = []
    for variable in variables:
        if variable.split(".")[0] == 'meta':
            _resolve_meta_data(data, resolved_data, variable)
        else:
            _resolve_data(data, resolved_data, variable)
    return resolved_data


def _resolve_meta_data(data, resolved_data, variable):
    for index, datum in enumerate(data):
        len(resolved_data) > index or resolved_data.append({})
        resolved_data[index][variable] = datum[variable.split(".")[1]].value[variable.split(".")[2]]


def _resolve_data(data, resolved_data, variable):
    questionnaire_alias = variable.split(".")[0]
    question_path_components = variable.split(".")[1:]
    for index, datum in enumerate(data):
        value = _get_value(datum[questionnaire_alias].value["values"], question_path_components)
        len(resolved_data) > index or resolved_data.append({})
        resolved_data[index][variable] = value


def _get_value(values, question_path_components):
    if len(question_path_components) == 1:
        return values[question_path_components[0]]
    return _get_value(values[question_path_components[0]][0], question_path_components[1:])
