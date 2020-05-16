import xlrd


# 0 question - id вопроса,
# 1 formulation - id формулировки вопроса,
# 2 answer - номер выбранного ответа,
# 3 count - количество раз выбора данного ответа,
# 4 weight - вес данного ответа
# 5 student - id студента
def read_data_from_excel(path):
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(0)
    sheet.cell_value(0, 0)
    data = []
    for i in range(sheet.nrows):
        row = []
        for j in range(5):
            row.append(sheet.cell_value(i, j))
        data.append(row)
    return data


def read_raw_data_from_excel_KO(path):
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_name('db01-sort')
    data = []

    for i in range(1, sheet.nrows, 1):
        row = []
        question_id = (sheet.cell_value(i, 0), sheet.cell_value(i, 2))
        formulation_id = sheet.cell_value(i, 3)
        answer_id = sheet.cell_value(i, 6)
        weight = sheet.cell_value(i, 5)
        count = sheet.cell_value(i, 7)
        row.append(question_id)
        row.append(formulation_id)
        row.append(answer_id)
        row.append(count)
        row.append(weight)
        data.append(row)
    return data


def read_dictionary_from_excel(path):
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_name('inf-2018-19-1sem-questions')
    data = {}

    for i in range(1, sheet.nrows, 1):
        row = []
        question_key = sheet.cell_value(i, 3)

        val = data.get(question_key)
        if val is None:
            question_id = (sheet.cell_value(i, 1), sheet.cell_value(i, 4))
            formulation_id = sheet.cell_value(i, 5)
            distractor = sheet.cell_value(i, 8)
            row.append(question_id)
            row.append(formulation_id)
            row.append([distractor])
            data[question_key] = row
        else:
            distractor = sheet.cell_value(i, 8)
            data[question_key][2].append(distractor)
    return data


def read_raw_data_from_excel(path, dictionary):
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_name('inf-2018-19-1sem-tests')
    data = []

    for i in range(1, sheet.nrows, 1):
        row = []
        question_key = sheet.cell_value(i, 13)
        question = dictionary[question_key]
        formulation_id = question[1]
        answer_id = sheet.cell_value(i, 15)
        weight = sheet.cell_value(i, 16)
        student_id = sheet.cell_value(i, 7)
        row.append(question_key)
        row.append(formulation_id)
        row.append(answer_id)
        row.append(0)
        row.append(weight if answer_id != '' else 0)
        row.append(student_id)
        data.append(row)
    return data

