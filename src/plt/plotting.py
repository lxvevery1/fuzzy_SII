import matplotlib.pyplot as plt


def plot_input_sets(input_universe, input_sets, config):
    plt.figure(figsize=(12, 5))
    for name, values in input_sets.items():
        plt.plot(input_universe, values, label=name)
    plt.title("Входные переменные")
    plt.xlabel(config["input_name"])
    plt.ylabel("Уровень принадлежности")
    plt.legend()
    plt.show()


def plot_output_sets(output_universe, output_sets, config):
    plt.figure(figsize=(12, 5))
    for name, values in output_sets.items():
        plt.plot(output_universe, values, label=name)
    plt.title("Выходные множества")
    plt.xlabel(config["output_name"])
    plt.ylabel("Уровень принадлежности")
    plt.legend()
    plt.show()


def plot_implication_methods(
    input_values,
    output_values_mamdani,
    output_values_larsen,
    output_values_premise_truth,
    example_input_value,
    mamdani_result,
    larsen_result,
    premise_truth_result,
    config,
):
    plt.figure(figsize=(12, 5))
    plt.plot(input_values, output_values_mamdani, label="Метод Мамдани", color="blue")
    plt.plot(
        input_values,
        output_values_larsen,
        label="Метод Ларсена",
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

    plt.scatter(
        [example_input_value] * 3,  # Тот же вход для всех методов
        [mamdani_result, larsen_result, premise_truth_result],  # Результаты
        color=["blue", "orange", "green"],
        label=[
            "Результат Мандани",
            "Результат Ларсена",
            "Результат истинности предпосылки",
        ],
        zorder=5,  # Поверх линий
    )

    plt.title("Методы импликации")
    plt.xlabel(config["input_name"])
    plt.ylabel(config["output_name"])
    plt.legend()
    plt.show()
