import pandas as pd


def process_file(filename):
    # Матрицы для хранения данных
    A1 = {}
    A2 = {}
    A3 = {}
    B = {}
    rules = []
    given = []
    given1 = []

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    current_set_name = None
    current_set_values = []
    current_set_length = 0
    set = 0
    given_set = 0
    a1_name = ""
    a2_name = ""
    a3_name = ""
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
                if set == 1:
                    A1[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values)
                    )
                elif set == 2:
                    A2[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values)
                    )
                elif set == 3:
                    A3[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values)
                    )
                elif set == 4:
                    B[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values)
                    )

            set += 1

            # Начинаем обработку нового множества
            parts = line.split()
            current_set_name = parts[-1]
            if set == 1:
                a1_name = current_set_name
            elif set == 2:
                a2_name = current_set_name
            elif set == 3:
                a3_name = current_set_name
            elif set == 4:
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
                if set == 1:
                    A1[fuzzy_set_name] = fuzzy_set_values
                elif set == 2:
                    A2[fuzzy_set_name] = fuzzy_set_values
                elif set == 3:
                    A3[fuzzy_set_name] = fuzzy_set_values
                elif set == 4:
                    B[fuzzy_set_name] = fuzzy_set_values

        elif line.startswith("Если"):
            # Обработка правила
            parts = line.split()
            antecedent1 = parts[2]
            antecedent2 = parts[5]
            antecedent3 = parts[8]
            consequent = parts[-1]
            rules.append((antecedent1, antecedent2, antecedent3, consequent))

        elif line.startswith("Пусть"):
            # Обработка начального состояния
            i += 1
            line = lines[i].strip()
            values = list(map(float, line.split()))
            given1.extend(values)
            given.append(given1)
            given1 = []

        i += 1

    # Обрабатываем последнее множество
    if current_set_name:
        if set == 1:
            A1[current_set_name] = current_set_values + [0] * (
                current_set_length - len(current_set_values)
            )
        elif set == 2:
            A2[current_set_name] = current_set_values + [0] * (
                current_set_length - len(current_set_values)
            )
        elif set == 3:
            A3[current_set_name] = current_set_values + [0] * (
                current_set_length - len(current_set_values)
            )
        elif set == 4:
            B[current_set_name] = current_set_values + [0] * (
                current_set_length - len(current_set_values)
            )

    # Преобразуем матрицу множеств в DataFrame
    A1 = pd.DataFrame(A1)
    A2 = pd.DataFrame(A2)
    A3 = pd.DataFrame(A3)
    B = pd.DataFrame(B)

    A = []
    A.append([])
    A.append(A1)
    A.append(A2)
    A.append(A3)

    name = []
    name.append(b_name)
    name.append(a1_name)
    name.append(a2_name)
    name.append(a3_name)

    # Преобразуем правила в DataFrame
    rules = pd.DataFrame(rules, columns=[a1_name, a2_name, a3_name, b_name])

    return A, B, rules, given, name


def get_outputs(B, rules, name, levels_of_truth):
    outputs = []
    for r in range(len(rules[name[0]])):
        output = []
        for i in range(len(B[rules[name[0]][r]])):
            output.append(min(B[rules[name[0]][r]][i], levels_of_truth[r]))

        print(f"Выход для правила {r+1}")
        print([float(value) for value in output])
        outputs.append(output)

    print("")
    return outputs


def outputs_aggregation(outputs):
    aggregation = []
    for i in range(len(outputs[0])):
        max_output = outputs[0][i]
        for output in outputs:
            max_output = max(max_output, output[i])
        aggregation.append(max_output)

    print("\nАггрегация выходов")
    aggregation = [max(output[i] for output in outputs) for i in range(len(outputs[0]))]
    print([float(value) for value in aggregation])
    print("")
    return aggregation


def defuzzification(A, B, name, given, aggregation):
    for j in range(3):
        sum_1 = 0
        sum_2 = 0
        for i in range(len(given)):
            sum_1 += given[j][i] * A[j + 1][name[j + 1]][i]
            sum_2 += given[j][i]
        mid = sum_1 / sum_2
        print(f"Четкое значение входа {name[j+1]}: {round(mid)}")

    sum_1 = 0
    sum_2 = 0
    for i in range(len(aggregation)):
        sum_1 += aggregation[i] * B[name[0]][i]
        sum_2 += aggregation[i]
    mid = sum_1 / sum_2
    print(f"Четкое значение выхода {name[0]}: {round(mid)}")
    print("\n")


def maxmin(a, b):
    row = []
    for i in range(len(a)):
        row.append(min(a[i], b[i]))
    output = max(row)
    return output


def levels_of_truth_of_premises(A, B, rules, given, name):
    levels_of_truth = []
    for i in range(len(rules[name[0]])):
        a1 = A[1][rules[name[1]][i]]
        a2 = A[2][rules[name[2]][i]]
        a3 = A[3][rules[name[3]][i]]

        level_a1 = maxmin(a1, given[0])
        level_a2 = maxmin(a2, given[1])
        level_a3 = maxmin(a3, given[2])

        level = min(level_a1, level_a2, level_a3)
        levels_of_truth.append(level)

    print("Уровни истинности предпосылок правил:")
    print([float(value) for value in levels_of_truth])
    print("")
    return levels_of_truth


filename = "config_many.txt"
A, B, rules, given, name = process_file(filename)

print("\nМатрица множеств А1:")
print(A[1])
print("\nМатрица множеств А2:")
print(A[2])
print("\nМатрица множеств А3:")
print(A[3])
print("\nМатрица множеств B:")
print(B)
print("\nМатрица правил:")
print(rules)
print("\nПусть:")
print(given)
print("")

levels_of_truth = levels_of_truth_of_premises(A, B, rules, given, name)
outputs = get_outputs(B, rules, name, levels_of_truth)
aggregation = outputs_aggregation(outputs)
defuzzification(A, B, name, given, aggregation)
