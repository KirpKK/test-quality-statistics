import math

from scipy.stats import chi2


# 0 question - id вопроса,
# 1 formulation - id формулировки вопроса,
# 2 answer - номер выбранного ответа,
# 3 count - количество раз выбора данного ответа,
# 4 weight - вес данного ответа,
# 5 student_id - id студента,

# подсчитывает, сколько раз был задан вопрос в данной формулировке и количество верных ответов
def count_formulation_stat(data, dictionary):
    result = {}
    for i in data:
        question = dictionary[i[0]][0]
        key = (question, i[1])
        val = result.get(key)
        if val is None:
            result[key] = [i[3], i[3] * i[4]]
        else:
            result[key] = [val[0] + i[3], val[1] + i[3] * i[4]]
    return result


#  подсчитывает статистику для критерия однородности КО-I
def test_formulation_homogeneity(formulation_stat):
    keys = get_key_list(formulation_stat)
    keys.sort()
    result = []
    for index1 in range(len(keys)):
        res = []
        for index2 in range(index1 + 1):
            if index1 == index2:
                res.append(0)
            else:
                val1 = formulation_stat[keys[index1]]
                val2 = formulation_stat[keys[index2]]
                p1 = val1[1] / val1[0]
                p2 = val2[1] / val2[0]
                q_denominator = math.sqrt(p1 * (1 - p1) / val1[0] + p2 * (1 - p2) / val2[0])
                if q_denominator == 0:
                    q = 0
                else:
                    q = round(math.fabs(p1 - p2) / q_denominator, 3)
                res.append(q)
        result.append(res)
    return result, keys


# составляет список ключей для словаря
def get_key_list(dictionary):
    result = []
    keys = dictionary.keys()
    for k in keys:
        result.append(k)
    return result


# возвращает словарь, содержащий статистики по формулировкам для отдельного вопроса
def get_question_formulation_stat(formulation_stat):
    return group_stat_by_question(formulation_stat)


# принимает словарь с ключом [вопрос, ...]
# возвращает словарь вида: вопрос  -  [[формулировка] - stat1,
#                                     [формулировка] - stat2,
#                                     ...]
def group_stat_by_question(stat):
    result = {}
    for key, val in stat.items():
        if result.get(key[0]) is None:
            result[key[0]] = {key[1]: val}
        else:
            result[key[0]][key[1]] = val
    return result


# возвращает словарь вида: студент  -  тест: (вопрос: вес ответа, ...)),
#                                       тест: (вопрос: вес ответа, ...))
def group_stat_by_student(data, dictionary):
    result = {}
    for row in data:
        question = dictionary[row[0]][0]
        if result.get(row[5]) is None:
            result[row[5]] = {question[0]: {question[1]: row[4]}}
        else:
            if result[row[5]].get(question[0]) is None:
                result[row[5]][question[0]] = {question[1]: row[4]}
            else:
                result[row[5]][question[0]][question[1]] = row[4]

    return result


#  подсчитывает статистику для критерия однородности КО-II
#
# Корректность проведения теста хи-квадрат определяется двумя условиями:
# ожидаемые частоты < 5 должны встречаться не более чем в 20% полей таблицы;
# суммы по строкам и столбцам всегда должны быть больше нуля.
# => min_frequency = 5, max_percentage = 20
def test_distractor_homogeneity(distractor_frequency_stat, p_value, min_frequency, max_percentage):
    data = dict.copy(distractor_frequency_stat)
    for key, val in data.items():
        keys = get_key_list(val)
        (column_data, row_data, sum, is_correct) = get_theoretical_data_for_question(val, keys, min_frequency,
                                                                                     max_percentage)

        data[key] = ok(column_data, row_data, sum, is_correct, keys, val, p_value)
    return data


def ok(column_data, row_data, sum, is_correct, keys, val, p_value):
    if is_correct:
        result = 0
        for row in range(len(keys)):
            for column in range(len(val[keys[row]])):
                theoretical_value = row_data[row] * column_data[column] / sum
                result += math.pow(val[keys[row]][column][0] - theoretical_value, 2) / theoretical_value
        df = (len(keys) - 1) * (len(val[keys[row]]) - 1)
        return (round(math.fabs(result), 3), chi2.isf(p_value, df))
    else:
        return None


# возвращает словарь вида: вопрос - {формулировка - ([отсортированные (частота, формулировка)])}
def get_distractor_frequency_stat(data, dictionary):
    structured_data = get_structured_data(data, dictionary)
    grouped_structured_data = group_stat_by_question(structured_data)
    sorted_grouped_structured_data = sort_by_formulation_frequency(grouped_structured_data)
    return sorted_grouped_structured_data


# возвращает словарь с ключом (вопрос, формулировка), содержащий частоты верного ответа и дистракторов (ответ, частота, вес)
def get_structured_data(data, dictionary):
    result = {}
    for i in data:
        key = (dictionary[i[0]][0], i[1])
        val = result.get(key)
        if val is None:
            row = []
            for answer in dictionary[i[0]][2]:
                row.append([answer, 0, 0])
            result[key] = row
        for answer in result[key]:
            if answer[0] == i[2]:
                answer[1] = i[3]
                answer[2] = i[4]
    return result


# сортирует словарь, содержащий статистики по формулировкам для отдельного вопроса
# первый - правильный ответ, далее - дистракторы по убыванию частоты выбора
def sort_by_formulation_frequency(grouped_structured_data):
    for key_question, stat_question in grouped_structured_data.items():
        for key_formulation, stat_formulation in stat_question.items():
            stat_question[key_formulation] = sort(stat_formulation)
    return grouped_structured_data


# принимает массив значений вида [ответ, частота, вес]
# возвращает массив вида [частота правильного ответа, далее - дистракторы по убыванию частоты выбора]
def sort(grouped_structured_data):
    distractors = []
    for val in grouped_structured_data:
        if val[2] == 0:
            distractors.append((val[1], val[0]))
    distractors.sort(key=lambda value: value[0])
    distractors.reverse()
    return distractors


def get_theoretical_data_for_question(distractor_frequency_stat, keys, edge, less_then_edge_percentage):
    column_data = []
    row_data = []
    sum = 0
    count_less_then_edge = 0
    count_is_zero = 0
    for row_index in range(len(keys)):
        for column_index in range(len(distractor_frequency_stat[keys[row_index]])):
            val = distractor_frequency_stat[keys[row_index]][column_index][0]
            if val < edge:
                count_less_then_edge += 1
            row_val = row_data[row_index] if row_index < len(row_data) else None
            if row_val is None:
                row_data.append(val)
                if val == 0:
                    count_is_zero += 1
            else:
                row_data[row_index] = row_val + val
                if row_val == 0 and val > 0:
                    count_is_zero -= 1

            column_val = column_data[column_index] if column_index < len(column_data) else None
            if column_val is None:
                column_data.append(val)
                if val == 0:
                    count_is_zero += 1
            else:
                column_data[column_index] = column_val + val
                if column_val == 0 and val > 0:
                    count_is_zero -= 1
            sum += val
    is_correct = count_is_zero == 0 and count_less_then_edge <= len(keys) * len(
        distractor_frequency_stat[keys[row_index]]) * less_then_edge_percentage / 100
    return (column_data, row_data, sum, is_correct)


def get_correlation_matrix(test, data_by_student):
    result = {}
    for test_id, question_list in test.items():
        question_list.sort()
        matrix = []
        for index1 in range(len(question_list)):
            res = []
            for index2 in range(index1 + 1):
                if index1 == index2:
                    res.append(1)
                else:
                    correlation = get_correlation(data_by_student, test_id, question_list[index1],
                                                  question_list[index2])
                    res.append(correlation)
            matrix.append(res)
        result[test_id] = (matrix, question_list)
    return result


def get_correlation(data_by_student, test_id, index1, index2):
    count12 = 0
    count1 = 0
    count2 = 0
    count_all = 0
    for key, elem in data_by_student.items():
        if test_id in elem.keys():
            if index1 in elem[test_id].keys() and index2 in elem[test_id].keys():
                count_all += 1
                if elem[test_id][index1] == 1 and elem[test_id][index2] == 1:
                    count12 += 1
                if elem[test_id][index1] == 1:
                    count1 += 1
                if elem[test_id][index2] == 1:
                    count2 += 1
    if count_all == 0:
        cor = "-"
    else:
        p1 = count1 / count_all
        p2 = count2 / count_all
        p12 = count12 / count_all

        cor_denominator = math.sqrt(p1 * (1 - p1) * p2 * (1 - p2))
        if cor_denominator == 0:
            cor = "-"
        else:
            cor = round((p12 - p1 * p2) / cor_denominator, 3)
    return cor
