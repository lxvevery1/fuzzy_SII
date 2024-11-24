import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import json
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Загрузка конфигурации
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

# Универсумы входных и выходных переменных
input_universe = np.arange(0, config["input_max"] + 1, 1)
output_universe = np.arange(0, config["output_max"] + 1, 1)


# Функции принадлежности для входа и выхода
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
                            if x < params[1]
                            else (params[2] - x) / (params[2] - params[1])
                        ),
                    ),
                )
                for x in universe
            ]
        )
    return fuzzy_sets


input_sets = create_fuzzy_sets(input_universe, config["input_sets"])
output_sets = create_fuzzy_sets(output_universe, config["output_sets"])


# Методы импликации
def mandani_implication(truth_value, output_set):
    return np.minimum(truth_value, output_set)


def zadeh_implication(truth_value, output_set):
    return np.maximum(truth_value, output_set)


def premise_truth_implication(truth_value, output_set):
    """Метод истинности предпосылки: используется минимум всех истинностей для входных условий"""
    return truth_value * output_set


# Оценка результата для каждого метода
def evaluate(input_value, method):
    # Степени истинности для входа
    input_truths = {name: input_sets[name][int(input_value)] for name in input_sets}

    # Агрегация выходного множества
    aggregated_output = np.zeros_like(output_universe)
    for rule in config["rules"]:
        antecedent_truth = min(input_truths[cond] for cond in rule["antecedents"])
        consequent_set = output_sets[rule["consequent"]]

        if method == "mandani":
            implication_result = mandani_implication(antecedent_truth, consequent_set)
        elif method == "zadeh":
            implication_result = zadeh_implication(antecedent_truth, consequent_set)
        elif method == "premise_truth":
            implication_result = premise_truth_implication(
                antecedent_truth, consequent_set
            )
        else:
            raise ValueError(f"Неизвестный метод: {method}")

        aggregated_output = np.maximum(aggregated_output, implication_result)

    # Дефаззификация методом центра тяжести
    if np.sum(aggregated_output) > 0:
        result = np.sum(aggregated_output * output_universe) / np.sum(aggregated_output)
    else:
        result = 0
    return result, aggregated_output


# Генерация данных
input_values = np.linspace(0, config["input_max"], 100)
results_mandani = [evaluate(i, "mandani") for i in input_values]
results_zadeh = [evaluate(i, "zadeh") for i in input_values]
results_premise_truth = [evaluate(i, "premise_truth") for i in input_values]

output_values_mandani = [res[0] for res in results_mandani]
output_values_zadeh = [res[0] for res in results_zadeh]
output_values_premise_truth = [res[0] for res in results_premise_truth]

# Визуализация с использованием matplotlib и seaborn
sns.set_theme(style="whitegrid")
plt.figure(figsize=(12, 8))

# Входные переменные
plt.subplot(3, 1, 1)
for name, values in input_sets.items():
    plt.plot(input_universe, values, label=name)
plt.title("Входные переменные")
plt.legend()

# Выходные множества
plt.subplot(3, 1, 2)
for name, values in output_sets.items():
    plt.plot(output_universe, values, label=name)
plt.title("Выходные множества")
plt.legend()

# Зависимость методов импликации
plt.subplot(3, 1, 3)
plt.plot(input_values, output_values_mandani, label="Метод Мандани", color="blue")
plt.plot(
    input_values,
    output_values_zadeh,
    label="Метод Заде",
    color="orange",
    linestyle="--",
)
plt.plot(
    input_values,
    output_values_premise_truth,
    label="Метод истинности предпосылки",
    color="green",
    linestyle=":",
)
plt.title("Методы импликации")
plt.xlabel(config["input_name"])
plt.ylabel(config["output_name"])
plt.legend()

plt.tight_layout()
plt.show()

# 3D визуализация с Plotly
fig = go.Figure()
fig.add_trace(
    go.Scatter3d(
        x=input_values,
        y=output_values_mandani,
        z=np.zeros_like(output_values_mandani),
        mode="lines",
        name="Мандани",
        line=dict(color="blue"),
    )
)
fig.add_trace(
    go.Scatter3d(
        x=input_values,
        y=output_values_zadeh,
        z=np.zeros_like(output_values_zadeh),
        mode="lines",
        name="Заде",
        line=dict(color="orange"),
    )
)
fig.add_trace(
    go.Scatter3d(
        x=input_values,
        y=output_values_premise_truth,
        z=np.zeros_like(output_values_premise_truth),
        mode="lines",
        name="Метод истинности предпосылки",
        line=dict(color="green"),
    )
)
fig.update_layout(
    title="Сравнение методов импликации",
    scene=dict(
        xaxis_title=config["input_name"],
        yaxis_title=config["output_name"],
        zaxis_title="Метод",
    ),
)
fig.show()

logging.info("Программа завершена.")
