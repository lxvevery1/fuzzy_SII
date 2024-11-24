import json
import logging

import matplotlib.pyplot as plt
import numpy as np

# Настройка логирования для отслеживания работы программы
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Загрузка конфигурации из файла
try:
    with open("config_1.json") as f:
        config = json.load(f)
        logging.info("Конфигурация загружена успешно.")
except FileNotFoundError:
    logging.error("Файл конфигурации 'config_1.json' не найден.")
    raise
except json.JSONDecodeError:
    logging.error("Ошибка при разборе конфигурационного файла JSON.")
    raise

# Определяем входные и выходные переменные
input_universe = np.arange(0, config["input_max"] + 1, 1)
output_universe = np.arange(0, config["output_max"] + 1, 1)

# Создаём функции принадлежности вручную
input_sets = {
    name: np.array(
        [
            max(
                0,
                min(
                    1,
                    (
                        (x - params[0]) / (params[1] - params[0])
                        if x < params[1]
                        else (params[2] - x) / (params[2] - params[1])
                    ),
                ),
            )
            for x in input_universe
        ]
    )
    for name, params in config["input_sets"].items()
}

output_sets = {
    name: np.array(
        [
            max(
                0,
                min(
                    1,
                    (
                        (x - params[0]) / (params[1] - params[0])
                        if x < params[1]
                        else (params[2] - x) / (params[2] - params[1])
                    ),
                ),
            )
            for x in output_universe
        ]
    )
    for name, params in config["output_sets"].items()
}


# Определяем правила с использованием импликации Заде
def zadeh_implication(input_values, output_set):
    """
    Реализация импликации Заде:
    Использует максимум степени истинности входного условия для вывода.
    """
    result = np.zeros_like(output_set)
    for i, truth_value in enumerate(input_values):
        result = np.maximum(result, np.minimum(truth_value, output_set))
    return result


# Оценка входных данных с применением правил
def evaluate(input_value):
    logging.info(f"Оценка для входного значения: {input_value}")

    # Расчёт степени истинности для входных переменных
    input_truths = {name: input_sets[name][int(input_value)] for name in input_sets}
    logging.debug(f"Степени истинности для входа: {input_truths}")

    # Применение правил
    output_aggregation = np.zeros_like(output_universe)
    for rule in config["rules"]:
        antecedent_truth = min(input_truths[cond] for cond in rule["antecedents"])
        consequent_set = output_sets[rule["consequent"]]
        logging.debug(
            f"Применение правила: {rule['antecedents']} -> {rule['consequent']}"
        )

        # Импликация Заде
        output_rule = zadeh_implication([antecedent_truth], consequent_set)
        output_aggregation = np.maximum(output_aggregation, output_rule)

    # Центр тяжести для дефаззификации
    result = (
        np.sum(output_aggregation * output_universe) / np.sum(output_aggregation)
        if np.sum(output_aggregation) != 0
        else 0
    )
    logging.info(f"Оценка завершена. Выходное значение: {result:.2f}")
    return result


# Пример использования с множеством входных значений
input_values = np.linspace(0, config["input_max"], 100)
output_values = [evaluate(i) for i in input_values]

# Визуализация входных и выходных переменных
plt.figure(figsize=(12, 8))

# Входные множества
plt.subplot(3, 1, 1)
for name, values in input_sets.items():
    plt.plot(input_universe, values, label=name)
plt.title("Входные переменные")
plt.legend()

# Выходные множества
plt.subplot(3, 1, 2)
for name, values in output_sets.items():
    plt.plot(output_universe, values, label=name)
plt.title("Выходные переменные")
plt.legend()

# График зависимости входа от выхода
plt.subplot(3, 1, 3)
plt.plot(input_values, output_values, label="Зависимость входа от выхода")
plt.title("Зависимость входных значений от выходных")
plt.xlabel(config["input_name"])
plt.ylabel(config["output_name"])
plt.legend()

plt.tight_layout()
plt.show()

logging.info("Процесс завершен успешно.")
