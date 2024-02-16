class QueryProcess:
    def __init__(self):
        pass

    def query_answer(self, raw_result):

        formatted_rows = ''
        for i, row in enumerate(raw_result):
            formatted_rows += f"{i + 1}: "
            for i, col in enumerate(row):
                if col:
                    formatted_rows += ''.join(char if char.isascii() else ':' for char in str(col))
                else:
                    formatted_rows += '(unavailable)'
                if i + 1 < len(row):
                    formatted_rows += ', '
                # print(col, sep='')
            formatted_rows += '. \n'

        return formatted_rows
