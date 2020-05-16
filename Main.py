import os
from docx import Document

import DataPrinter
import DataReader
import Stat

# 0 question - id вопроса,
# 1 formulation - id формулировки вопроса,
# 2 answer - номер выбранного ответа,
# 3 count - количество раз выбора данного ответа,
# 4 weight - вес данного ответа,

data_stub = [
    [1, 1, 1, 2, 0],
    [1, 1, 2, 1, 0],
    [1, 1, 3, 2, 1],
    [1, 2, 1, 3, 0],
    [1, 2, 2, 0, 1],
    [1, 2, 3, 2, 0],

    [2, 1, 'a', 0, 0],
    [2, 1, 'b', 2, 1],
    [2, 1, 'c', 1, 0],
    [2, 'q', 'a', 3, 0],
    [2, 'q', 'b', 2, 1],
    [2, 'q', 'c', 1, 0],
    [2, 'w', 'a', 1, 0],
    [2, 'w', 'b', 0, 1],
    [2, 'w', 'c', 0, 0],

    [3, 1, 1, 1, 0],
    [3, 1, 2, 2, 1],
    [3, 1, 3, 1, 0],
    [3, 2, 1, 0, 0],
    [3, 2, 2, 3, 1],
    [3, 2, 4, 2, 0],

    [4, 1, 1, 1, 0],
    [4, 1, 2, 2, 1],
    [4, 1, 3, 1, 0],
    [4, 2, 1, 1, 0],
    [4, 2, 2, 2, 1],
    [4, 2, 4, 1, 0]
]


def main():
    path = "/Users/u15672269/stat"
    data_path = "/Users/u15672269/Desktop/For_Kseniya/однородность.xls"
    title = "Отчет о показателях качества тестовых заданий по курсу Информатика 2018-2019 учебного года 1 семестра"
    KO_I = True
    KO_II = True
    correlation = True

    report = Document()
    report.add_heading(title, 0)

    if (KO_I or KO_II or correlation):
        dictionary = DataReader.read_dictionary_from_excel(data_path)
        data = DataReader.read_raw_data_from_excel(data_path, dictionary)

        data_KO = []
        keys = []
        # состав вопросов в тесте
        test = {}
        for i in data:
            if i[2] != '':
                question = dictionary[i[0]][0]
                val = test.get(question[0])
                if val is None:
                    test[question[0]] = list()
                    test[question[0]].append(question[1])
                else:
                    if question[1] not in test[question[0]]:
                        test[question[0]].append(question[1])

                key = (question, i[1], i[2])
                if key not in keys:
                    count = sum(elem[0] == i[0] and elem[1] == key[1] and elem[2] == key[2] for elem in data)
                    data_KO.append([i[0], i[1], i[2], count, i[4], i[5]])
                    keys.append(key)
        print("ok")

    if KO_I:
        print("KO_I processing started")
        formulation_stat = Stat.get_question_formulation_stat(Stat.count_formulation_stat(data_KO, dictionary))
        formulation_homogeneity = {}
        for key, question_stat in formulation_stat.items():
            formulation_homogeneity[key] = Stat.test_formulation_homogeneity(question_stat)
        DataPrinter.create_report_KO_I(report, formulation_homogeneity, path)
        print("KO_I processing finished")

    if KO_II:
        print("KO_II processing started")
        distractor_frequency_stat = Stat.get_distractor_frequency_stat(data_KO, dictionary)
        distractor_homogeneity = Stat.test_distractor_homogeneity(distractor_frequency_stat, 0.05, 0, 100)
        DataPrinter.create_report_KO_II(report, distractor_frequency_stat, distractor_homogeneity, path)
        print("KO_II processing finished")

    if correlation:
        print("correlation processing started")
        correlation_stat = Stat.get_correlation_matrix(test, Stat.group_stat_by_student(data, dictionary))
        DataPrinter.create_report_correlation(report, correlation_stat, path)
        print("correlation processing finished")


    report.save(os.path.join(path, '{}.docx'.format(title)))

    return


if __name__ == '__main__':
    main()
