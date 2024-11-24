import json
import logging

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import skfuzzy as fuzz
from plotly.subplots import make_subplots
from skfuzzy import control as ctrl

# Настройка логирования для отслеживания работы программы
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
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
input_var = ctrl.Antecedent(
    np.arange(0, config["input_max"] + 1, 1), config["input_name"]
)
output_var = ctrl.Consequent(
    np.arange(0, config["output_max"] + 1, 1), config["output_name"]
)

# Определяем множества для входных переменных
for name, params in config["input_sets"].items():
    input_var[name] = fuzz.trimf(input_var.universe, params)

# Определяем множества для выходных переменных
for name, params in config["output_sets"].items():
    output_var[name] = fuzz.trimf(output_var.universe, params)

# Определяем правила
rules = []
for rule in config["rules"]:
    antecedent = None
    for condition in rule["antecedents"]:
        if antecedent is None:
            antecedent = input_var[condition]
        else:
            antecedent = antecedent & input_var[condition]
    consequent = output_var[rule["consequent"]]
    rules.append(ctrl.Rule(antecedent, consequent))
    logging.debug(f"Правило создано: {rule['antecedents']} -> {rule['consequent']}")

# Создаем систему управления
control_system = ctrl.ControlSystem(rules)
evaluation = ctrl.ControlSystemSimulation(control_system)
logging.info("Система управления и объект оценки созданы.")


# Функция для оценки на основе входного значения
def evaluate(input_value):
    evaluation.input[config["input_name"]] = input_value
    evaluation.compute()
    return evaluation.output[config["output_name"]]


# Пример использования с множеством входных значений
input_values = np.linspace(0, config["input_max"], 100)
output_values = [evaluate(i) for i in input_values]

# Визуализация с использованием Plotly
fig = make_subplots(
    rows=3,
    cols=1,
    subplot_titles=[
        f"Функции принадлежности для {config['input_name']}",
        f"Функции принадлежности для {config['output_name']}",
        "Зависимость входных значений от выходных",
    ],
)

# Визуализация 1: Функции принадлежности входных переменных
for name in input_var.terms:
    fig.add_trace(
        go.Scatter(
            x=input_var.universe,
            y=input_var[name].mf,
            mode="lines",
            name=f"{config['input_name']}: {name}",
            line=dict(width=2),
        ),
        row=1,
        col=1,
    )

# Визуализация 2: Функции принадлежности выходных переменных
for name in output_var.terms:
    fig.add_trace(
        go.Scatter(
            x=output_var.universe,
            y=output_var[name].mf,
            mode="lines",
            name=f"{config['output_name']}: {name}",
            line=dict(width=2),
        ),
        row=2,
        col=1,
    )

# Визуализация 3: Зависимость входных значений от выходных
fig.add_trace(
    go.Scatter(
        x=input_values,
        y=output_values,
        mode="lines+markers",
        marker=dict(size=6, color="red"),
        line=dict(color="blue", width=3),
        name="Вход -> Выход",
    ),
    row=3,
    col=1,
)

# Общие настройки графиков
fig.update_layout(
    height=900,
    title_text="Современная визуализация нечёткой логики",
    title_font=dict(size=24, family="Arial, sans-serif", color="darkblue"),
    plot_bgcolor="whitesmoke",
    legend=dict(font=dict(size=12)),
    margin=dict(l=40, r=40, t=40, b=40),
)

# Настройки осей
fig.update_xaxes(title_text=config["input_name"], row=1, col=1)
fig.update_yaxes(title_text="Степень принадлежности", row=1, col=1)
fig.update_xaxes(title_text=config["output_name"], row=2, col=1)
fig.update_yaxes(title_text="Степень принадлежности", row=2, col=1)
fig.update_xaxes(title_text=config["input_name"], row=3, col=1)
fig.update_yaxes(title_text=config["output_name"], row=3, col=1)

# Показ графиков
fig.show()

# Логирование завершения процесса
logging.info("Процесс завершен успешно.")
