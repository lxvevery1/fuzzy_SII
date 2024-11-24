import json
import logging

import numpy as np
import pandas as pd
import plotly.graph_objects as go

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

try:
    with open("config_1.json") as f:
        config = json.load(f)
        logging.info("Конфигурация загружена успешно.")
except FileNotFoundError:
    logging.error("Файл конфигурации 'config_1.json' не найден.")
    raise
except json.JSONDecodeError:
    logging.error("Ошибка при разборе JSON.")
    raise

input_universe = np.arange(0, config["input_max"] + 1, 1)
output_universe = np.arange(0, config["output_max"] + 1, 1)


def create_fuzzy_sets(universe, sets_config):
    fuzzy_sets = {}
    for name, params in sets_config.items():
        fuzzy_sets[name] = np.array(
            [
                max(
                    0,
                    min(
                        1,
                        (
                            (x - params[0]) / (params[1] - params[0])
                            if params[1] > params[0] and x < params[1]
                            else (
                                (params[2] - x) / (params[2] - params[1])
                                if params[2] > params[1]
                                else 0
                            )
                        ),
                    ),
                )
                for x in universe
            ]
        )
    return fuzzy_sets


input_sets = create_fuzzy_sets(input_universe, config["input_sets"])
output_sets = create_fuzzy_sets(output_universe, config["output_sets"])


def mandani_implication(truth_value, output_set):
    return np.minimum(truth_value, output_set)


def larsen_implication(truth_value, output_set):
    return np.minimum(1, np.maximum(0, truth_value + output_set - 1))


def premise_truth_implication(truth_value, output_set):
    return truth_value * output_set


def evaluate(input_value, method):
    input_truths = {name: input_sets[name][int(input_value)] for name in input_sets}

    aggregated_output = np.zeros_like(output_universe)
    for rule in config["rules"]:
        antecedent_truth = min(input_truths[cond] for cond in rule["antecedents"])
        consequent_set = output_sets[rule["consequent"]]

        if method == "mandani":
            implication_result = mandani_implication(antecedent_truth, consequent_set)
        elif method == "larsen":
            implication_result = larsen_implication(antecedent_truth, consequent_set)
        elif method == "premise_truth":
            implication_result = premise_truth_implication(
                antecedent_truth, consequent_set
            )
        else:
            raise ValueError(f"Неизвестный метод: {method}")

        # Выводим расчет импликации для каждого элемента матрицы
        print(f"Для правила {rule['antecedents']} -> {rule['consequent']}:")
        print(f"  Истинность предпосылки: {antecedent_truth:.2f}")
        print(f"  Множество следствия: {consequent_set}")
        print(f"  Результат импликации:")
        for i, output_value in enumerate(output_universe):
            print(f"    Для x = {output_value}: {implication_result[i]:.2f}")

        aggregated_output = np.maximum(aggregated_output, implication_result)

    return aggregated_output


def display_fuzzy_matrices():
    # Перебираем все правила и вычисляем нечеткие соответствия
    for rule in config["rules"]:
        antecedent_name = rule["antecedents"][0]
        consequent_name = rule["consequent"]

        antecedent_set = input_sets[antecedent_name]
        consequent_set = output_sets[consequent_name]

        # Вычисление нечеткого соответствия для каждого правила
        fuzzy_matrix = mandani_implication(antecedent_set, consequent_set)

        # Выводим матрицу нечеткого соответствия
        print(
            f"Матрица нечеткого соответствия для правила {antecedent_name} -> {consequent_name}:"
        )
        for i, output_value in enumerate(output_universe):
            print(f"  Для x = {output_value}: {fuzzy_matrix[i]:.2f}")
        print()

    # Агрегируем все выходные значения
    aggregated_outputs = [evaluate(i, "mandani") for i in input_universe]
    output_matrix = np.array(aggregated_outputs)

    # Создаем DataFrame для удобства
    df = pd.DataFrame(output_matrix, index=input_universe, columns=output_universe)
    print(f"Матрица агрегированных выходов (агрегация для метода Мамдани):")
    print(df)

    # Графическое отображение
    fig = go.Figure(
        data=[
            go.Surface(
                z=output_matrix,
                x=input_universe,
                y=output_universe,
                colorscale="Viridis",
            )
        ]
    )
    fig.update_layout(
        title=f"Агрегированная функция для метода Мамдани",
        scene=dict(
            xaxis_title="Входные значения",
            yaxis_title="Выходные значения",
            zaxis_title="Значения функции",
        ),
    )
    fig.show()


# Выводим матрицы нечетких соответствий и агрегированные выходы
display_fuzzy_matrices()
