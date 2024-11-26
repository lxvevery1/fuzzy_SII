import os
import sys

import pandas as pd

# Import script with plots drawings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import plt.plotting


def process_file(filename):
    # Матрицы для хранения данных
    A = {}
    B = {}
    rules = []
    given = []

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    current_set_name = None
    current_set_values = []
    current_set_length = 0
    A_set = False
    a_name = ""
    b_name = ""

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        elif line.startswith("Множество определения"):
            # Завершаем предыдущее множество, если оно есть
            if current_set_name:
                if A_set:
                    A[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values)
                    )
                else:
                    B[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values)
                    )

            A_set = not A_set

            # Начинаем обработку нового множества
            parts = line.split()
            current_set_name = parts[-1]
            if A_set:
                a_name = current_set_name
            else:
                b_name = current_set_name
            current_set_values = []
            current_set_length = 0

        elif line.startswith("0") or line.startswith("-") or line[0].isdigit():
            # Считываем числовые значения множества
            values = list(map(float, line.split()))
            if current_set_length == 0:
                current_set_length = len(values)
            current_set_values.extend(values)

        elif line.startswith("Нечеткое множество"):
            # Считываем название нечеткого множества
            parts = line.split()
            fuzzy_set_name = parts[-1]
            i += 1  # Переходим к следующей строке, содержащей значения
            if i < len(lines):
                fuzzy_set_values = list(map(float, lines[i].strip().split()))
                fuzzy_set_values.extend(
                    [0] * (current_set_length - len(fuzzy_set_values))
                )
                # Добавляем в матрицу множеств
                if A_set:
                    A[fuzzy_set_name] = fuzzy_set_values
                else:
                    B[fuzzy_set_name] = fuzzy_set_values

        elif line.startswith("Если"):
            # Обработка правила
            parts = line.split()
            antecedent = parts[2]  # Название нечеткого множества условия
            consequent = parts[-1]  # Название нечеткого множества результата
            rules.append((antecedent, consequent))

        elif line.startswith("Пусть"):
            # Обработка начального состояния
            i += 1
            line = lines[i].strip()
            values = list(map(float, line.split()))
            given.extend(values)

        i += 1

    # Обрабатываем последнее множество
    if current_set_name:
        if A_set:
            A[current_set_name] = current_set_values
        else:
            B[current_set_name] = current_set_values

    # Преобразуем матрицу множеств в DataFrame
    A = pd.DataFrame(A)
    B = pd.DataFrame(B)

    # Преобразуем правила в DataFrame
    rules = pd.DataFrame(rules, columns=["Условие", "Следствие"])

    return A, B, rules, given, a_name, b_name


def get_correspondences_Mamdani(A, B):
    print("===ИМПЛИКАЦИЯ МЕТОДОМ МАМДАНИ===")
    correspondences = []
    for r in range(len(rules["Условие"])):
        correspondence = []
        for i in range(len(A)):
            row = []
            for j in range(len(B)):
                row.append(min(A[rules["Условие"][r]][i], B[rules["Следствие"][r]][j]))
            correspondence.append(row)
        correspondences.append(correspondence)

    print("")
    for i, corr in enumerate(correspondences, start=1):
        print(f"Матрица зависимостей {i}")
        for row in corr:
            print([float(value) for value in row])
        print("")
    return correspondences


def get_correspondences_Larsen(A, B):
    print("===ИМПЛИКАЦИЯ МЕТОДОМ ЛАРСЕНА===")
    correspondences = []
    for r in range(len(rules["Условие"])):
        correspondence = []
        for i in range(len(A)):
            row = []
            for j in range(len(B)):
                row.append(
                    round(A[rules["Условие"][r]][i] * B[rules["Следствие"][r]][j], 2)
                )
            correspondence.append(row)
        correspondences.append(correspondence)

    print("")
    for i, corr in enumerate(correspondences, start=1):
        print(f"Матрица зависимостей {i}")
        for row in corr:
            print([float(value) for value in row])
        print("")
    return correspondences


def outputs_aggregation(correspondences, given):
    print("===ВЫЧИСЛЕНИЕ МЕТОДОМ АГРЕГАЦИИ ВЫХОДОВ===\n")
    outputs = []

    for num, correspondence in enumerate(correspondences, start=1):
        output = []
        for i in range(len(correspondence[0])):
            column = [min(given[j], correspondence[j][i]) for j in range(len(given))]
            output.append(max(column))

        print(f"Выход для правила {num}")
        print([float(value) for value in output])
        outputs.append(output)

    print("\nАггрегация выходов")
    aggregation = [max(output[i] for output in outputs) for i in range(len(outputs[0]))]
    print([float(value) for value in aggregation])
    return aggregation


def rules_aggregation(correspondences, given):
    print(f"===ВЫЧИСЛЕНИЕ МЕТОДОМ АГРЕГАЦИИ ПРАВИЛ===\n")
    aggregation = correspondences[0]
    for correspondence in correspondences:
        for i in range(len(A)):
            for j in range(len(B)):
                aggregation[i][j] = max(aggregation[i][j], correspondence[i][j])

    print(f"Агрегация правил")
    for i in range(len(aggregation)):
        print([float(value) for value in aggregation[i]])

    output = []
    for i in range(len(aggregation[0])):
        column = []
        for j in range(len(given)):
            column.append(min(given[j], aggregation[j][i]))
        output.append(max(column))

    print("")
    print(f"Значение выхода")
    print([float(value) for value in output])
    print("")
    return output


def defuzzification(output, values_a, a_name, given, values_b, b_name):
    sum_1 = 0
    sum_2 = 0
    for i in range(len(given)):
        sum_1 += given[i] * values_a[i]
        sum_2 += given[i]
    mid = sum_1 / sum_2
    print(f"ДЕФАЗАФИКАЦИЯ")
    print(f"Четкое значение входа {a_name}: {round(mid)}")
    sum_1 = 0
    sum_2 = 0
    for i in range(len(output)):
        sum_1 += output[i] * values_b[i]
        sum_2 += output[i]
    mid = sum_1 / sum_2
    print(f"Четкое значение выхода {b_name}: {round(mid)}")
    print("\n")


filename = "config_combined.txt"
A, B, rules, given, a_name, b_name = process_file(filename)

print("\nА:")
print(A)
print("\nB:")
print(B)
print("\nМатрица правил:")
print(rules)
print(f"\nПусть {a_name}:")
print(given)
print("")

input("Нажмите любую клавишу, чтобы посмотреть результат метода Мамдани...")

correspondences_M = get_correspondences_Mamdani(A, B)

input("Нажмите любую клавишу, чтобы посмотреть результат агрегации...")

output = outputs_aggregation(correspondences_M, given)
defuzzification(output, A[a_name], a_name, given, B[b_name], b_name)


output = rules_aggregation(correspondences_M, given)
defuzzification(output, A[a_name], a_name, given, B[b_name], b_name)

input("Нажмите любую клавишу, чтобы посмотреть результат метода Ларсена...")

correspondences_L = get_correspondences_Larsen(A, B)
output = outputs_aggregation(correspondences_L, given)
defuzzification(output, A[a_name], a_name, given, B[b_name], b_name)

input("Нажмите любую клавишу, чтобы посмотреть результат агрегации...")

output = rules_aggregation(correspondences_L, given)


input("Нажмите любую клавишу, чтобы посмотреть график...")
plt.plotting.plot_comparison_Q(correspondences_M, correspondences_L, A, B)
