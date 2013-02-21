NULL = '--'

class SubmissionFormatter(object):
    def get_formatted_values_for_list(self, values, tuple_format='%s<span class="small_grey">%s</span>', list_delimiter=', '):
        formatted_values = []
        for row in values:
            result = self._format_row(row, tuple_format, list_delimiter)
            formatted_values.append(list(result))
        return formatted_values

    def _format_row(self, row, tuple_format, list_delimiter):
        for each in row:
            if isinstance(each, tuple):
                new_val = tuple_format % (each[0], each[1]) if each[1] else each[0]
            elif isinstance(each, list):
                new_val = list_delimiter.join(each)
            elif each:
                new_val = each
            else:
                new_val = NULL
            yield new_val

